import asyncio
import json
import os
import shutil
import textwrap
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings
from app.schemas.ai_catalog import Character, PromptTemplate
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversations import (
    ConversationResponse,
    ConversationUpdate,
    ConversationWithCount,
    MessageResponse,
)
from app.services.ai_chat_db import AiChatDb, get_ai_chat_db, utc_now_iso
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service
from app.services.command_templates import (
    CommandTemplateService,
    get_command_template_service,
)
from app.services.settings import SettingsService, get_settings_service


class ChatService:
    def __init__(
        self,
        db: AiChatDb,
        settings_service: SettingsService,
        catalog_service: AiCatalogService,
        command_template_service: CommandTemplateService,
    ) -> None:
        self._lock = threading.RLock()
        self._db = db
        self._settings_service = settings_service
        self._catalog_service = catalog_service
        self._command_template_service = command_template_service

    async def chat(self, request: ChatRequest) -> ChatResponse:
        conversation_id, character, prompt_template, user_info = self._resolve_chat_session(request)
        workspace_dir = self._resolve_workspace_dir()
        claude_md, prompt = self._build_prompt(request, character, prompt_template, user_info)
        self._save_claude_md(claude_md, workspace_dir)
        response_text = await self._run_claude(prompt, request.model, workspace_dir)

        if request.no_save:
            return ChatResponse(
                conversation_id=-1,
                responses=[response_text],
                actions=[],
            )

        conversation_id = self._persist_chat(
            request,
            response_text,
            conversation_id,
            character.id,
            prompt_template.id,
            user_info,
        )
        return ChatResponse(
            conversation_id=conversation_id,
            responses=[response_text],
            actions=[],
        )

    def get_conversations(self) -> list[ConversationWithCount]:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            conversations = conn.execute(
                """
                SELECT
                    c.*,
                    COUNT(m.id) AS message_count
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY datetime(c.updated_at) DESC
                """
            ).fetchall()
            return [
                ConversationWithCount(
                    id=row["id"],
                    character_id=row["character_id"],
                    prompt_template_id=row["prompt_template_id"],
                    user_info=row["user_info"],
                    title=row["title"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    message_count=row["message_count"],
                )
                for row in conversations
            ]

    def get_conversation_by_id(self, conversation_id: int) -> ConversationResponse:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Conversation not found")
            return ConversationResponse(
                id=row["id"],
                character_id=row["character_id"],
                prompt_template_id=row["prompt_template_id"],
                user_info=row["user_info"],
                title=row["title"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> list[MessageResponse]:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            conversation = conn.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if conversation is None:
                raise RuntimeError("Conversation not found")

            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY datetime(created_at) ASC
                LIMIT ?
                """,
                (conversation_id, limit),
            ).fetchall()
            return [
                MessageResponse(
                    id=row["id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    content=row["content"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def update_conversation(
        self,
        conversation_id: int,
        conversation_data: ConversationUpdate,
    ) -> ConversationResponse:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            existing = conn.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if existing is None:
                raise RuntimeError("Conversation not found")

            next_title = existing["title"]
            next_user_info = existing["user_info"]
            if conversation_data.title is not None:
                next_title = conversation_data.title
            if conversation_data.user_info is not None:
                next_user_info = conversation_data.user_info

            conn.execute(
                """
                UPDATE conversations
                SET title = ?, user_info = ?, updated_at = ?
                WHERE id = ?
                """,
                (next_title, next_user_info, utc_now_iso(), conversation_id),
            )
            conn.commit()
            return self.get_conversation_by_id(conversation_id)

    def delete_conversation(self, conversation_id: int) -> None:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            existing = conn.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if existing is None:
                raise RuntimeError("Conversation not found")
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()

    def _resolve_chat_session(
        self,
        request: ChatRequest,
    ) -> tuple[int | None, Character, PromptTemplate, str]:
        # V2 parity:
        # - existing conversation always uses the stored character/template/user_info
        # - new conversation and no-save mode require explicit request ids
        conversation_id: int | None = None
        user_info = request.user_info or ""

        if not request.no_save and request.conversation_id is not None:
            with self._lock, self._db.with_lock(), self._db.connect() as conn:
                row = conn.execute(
                    "SELECT id, character_id, prompt_template_id, user_info FROM conversations WHERE id = ?",
                    (request.conversation_id,),
                ).fetchone()
            if row is None:
                raise RuntimeError("Conversation not found")
            conversation_id = int(row["id"])
            character_id = int(row["character_id"])
            prompt_template_id = int(row["prompt_template_id"])
            user_info = row["user_info"] or ""
        else:
            if request.character_id is None or request.prompt_template_id is None:
                raise RuntimeError("characterId and promptTemplateId are required for new conversation")
            character_id = request.character_id
            prompt_template_id = request.prompt_template_id

        character = next(
            (item for item in self._catalog_service.list_characters() if item.id == character_id),
            None,
        )
        prompt_template = next(
            (item for item in self._catalog_service.list_prompt_templates() if item.id == prompt_template_id),
            None,
        )

        if character is None:
            raise RuntimeError("Character not found")
        if prompt_template is None:
            raise RuntimeError("Prompt template not found")

        return conversation_id, character, prompt_template, user_info

    def _build_prompt(
        self,
        request: ChatRequest,
        character: Character,
        prompt_template: PromptTemplate,
        user_info: str,
    ) -> tuple[str, str]:
        user_name = request.user_name or ""
        character_name = character.name
        system_message = self._substitute(prompt_template.content, user_name, character_name)
        character_prompt = self._substitute(character.prompt_content, user_name, character_name)
        user_info = self._substitute(user_info, user_name, character_name)

        claude_md_parts = [
            "## System Message",
            "",
            system_message.strip(),
            "",
            "## Character",
            "",
            character_prompt.strip(),
            "",
        ]
        if user_info.strip():
            claude_md_parts.extend(["## User Information", "", user_info.strip(), ""])
        claude_md = "\n".join(claude_md_parts).strip() + "\n"

        command_info_list = [
            item.content for item in self._command_template_service.list_templates(is_active=1)
        ]
        history_block = self._format_history(request)
        current_input = request.system_context.strip() if request.system_context else request.message.strip()
        final_message = request.final_message.strip() if request.final_message else (
            "## Final Checkout\n\n- Check if all required tags are properly formatted\n- Ensure the response is concise and actionable\n"
        )
        now = datetime.now()
        weekday_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        current_time = (
            f"## Current Time\n{now.year}년 {now.month}월 {now.day}일 "
            f"{weekday_names[now.weekday()]} {now.hour}시 {now.minute}분"
        )

        full_message = textwrap.dedent(
            f"""
            {'## 명령어 정보\n\n' + '\n\n'.join(command_info_list) + '\n\n' if command_info_list else ''}
            <--Previous Exchanges Start-->

            {history_block}

            <--Previous Response End-->

            Do not include the content of this response, but continue the story after this response.

            ## Current Input

            ```

            {current_input}

            ```
            <--## Current Input End-->

            {final_message}

            {current_time}
            """
        ).strip()

        return claude_md, self._substitute(full_message, user_name, character_name)

    def _format_history(self, request: ChatRequest) -> str:
        if request.exclude_history:
            return "[이번 요청은 이전 대화 기록 없이 처리합니다]"

        if request.conversation_id is None:
            return "[Start a new chat]"

        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY datetime(created_at) ASC
                LIMIT 20
                """,
                (request.conversation_id,),
            ).fetchall()
            if not rows:
                return "[Start a new chat]"

            formatted: list[str] = []
            for row in rows:
                if row["role"] == "system":
                    continue
                role = "user" if row["role"] == "user" else "model"
                formatted.append(
                    json.dumps(
                        {
                            "role": role,
                            "timestamp": row["created_at"],
                            "parts": [{"text": row["content"]}],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            return ",\n".join(formatted) if formatted else "[Start a new chat]"

    def _persist_chat(
        self,
        request: ChatRequest,
        response_text: str,
        conversation_id: int | None,
        character_id: int,
        prompt_template_id: int,
        user_info: str,
    ) -> int:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            now = utc_now_iso()
            if conversation_id is not None:
                conn.execute(
                    """
                    UPDATE conversations
                    SET updated_at = ?, user_info = COALESCE(?, user_info)
                    WHERE id = ?
                    """,
                    (now, request.user_info, conversation_id),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO conversations (
                        character_id, prompt_template_id, user_info, title, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        character_id,
                        prompt_template_id,
                        user_info,
                        request.title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        now,
                        now,
                    ),
                )
                conversation_id = int(cursor.lastrowid)

            if request.role == "user":
                conn.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (conversation_id, "user", request.message, now),
                )
            conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, "assistant", response_text, now),
            )
            conn.commit()
            return conversation_id

    def _resolve_workspace_dir(self) -> Path:
        app_settings = self._settings_service.get_app_settings()
        if app_settings.claude_workspace_dir.strip():
            target = Path(app_settings.claude_workspace_dir.strip())
        else:
            settings = get_settings()
            # V2 defaults Claude CLI to the AppData root directory, not a workspace subfolder.
            target = settings.data_dir_path
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _save_claude_md(self, content: str, workspace_dir: Path) -> None:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        (workspace_dir / "CLAUDE.md").write_text(content, encoding="utf-8")

    async def _run_claude(self, prompt: str, model: str, workspace_dir: Path) -> str:
        claude_bin = os.getenv("AGI_VOICE_CLAUDE_BIN") or shutil.which("claude")
        if not claude_bin:
            raise RuntimeError("Claude CLI not found in PATH")

        process = await asyncio.create_subprocess_exec(
            claude_bin,
            "-p",
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
            "--model",
            model,
            "--disallowedTools",
            "TodoWrite,Task,Bash,WebSearch,WebFetch",
            cwd=str(workspace_dir),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
        )

        stdout, stderr = await process.communicate((prompt + "\n").encode("utf-8"))
        if process.returncode != 0:
            error_text = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(error_text or f"Claude CLI exited with {process.returncode}")

        response_text = self._extract_stream_json(stdout.decode("utf-8", errors="replace"))
        if not response_text.strip():
            raise RuntimeError("Claude CLI returned an empty response")
        return response_text

    def _extract_stream_json(self, stdout: str) -> str:
        full_response = ""
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = payload.get("type")
            if msg_type == "content_block_delta":
                delta = payload.get("delta", {})
                full_response += delta.get("text", "")
            elif msg_type == "assistant" and not full_response:
                content = payload.get("message", {}).get("content", [])
                if content:
                    full_response = content[0].get("text", "")
        return full_response

    def _substitute(self, text: str, user_name: str, character_name: str) -> str:
        return text.replace("{{user}}", user_name).replace("{{char}}", character_name)


_service = ChatService(
    get_ai_chat_db(),
    get_settings_service(),
    get_ai_catalog_service(),
    get_command_template_service(),
)


def get_chat_service() -> ChatService:
    return _service
