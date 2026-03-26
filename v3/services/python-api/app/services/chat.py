import asyncio
import json
import os
import shutil
import textwrap
import threading
from dataclasses import dataclass
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
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service
from app.services.command_templates import (
    CommandTemplateService,
    get_command_template_service,
)
from app.services.settings import SettingsService, get_settings_service


@dataclass
class ConversationMessage:
    role: str
    content: str
    created_at: str


@dataclass
class ConversationRecord:
    id: int
    character_id: int
    prompt_template_id: int
    title: str
    user_info: str | None
    created_at: str
    updated_at: str
    messages: list[ConversationMessage]


class ChatService:
    def __init__(
        self,
        storage_path: Path,
        settings_service: SettingsService,
        catalog_service: AiCatalogService,
        command_template_service: CommandTemplateService,
    ) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._settings_service = settings_service
        self._catalog_service = catalog_service
        self._command_template_service = command_template_service
        self._conversations: dict[int, ConversationRecord] = {}
        self._load()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        character, prompt_template = self._resolve_context(request)
        workspace_dir = self._resolve_workspace_dir()
        claude_md, prompt = self._build_prompt(request, character, prompt_template)
        self._save_claude_md(claude_md, workspace_dir)
        response_text = await self._run_claude(prompt, request.model, workspace_dir)

        if request.no_save:
            return ChatResponse(
                conversation_id=-1,
                responses=[response_text],
                actions=[],
            )

        conversation_id = self._persist_chat(request, response_text, character.id, prompt_template.id)
        return ChatResponse(
            conversation_id=conversation_id,
            responses=[response_text],
            actions=[],
        )

    def get_conversations(self) -> list[ConversationWithCount]:
        with self._lock:
            conversations = sorted(
                self._conversations.values(),
                key=lambda conversation: conversation.updated_at,
                reverse=True,
            )
            return [
                ConversationWithCount(
                    id=conversation.id,
                    character_id=conversation.character_id,
                    prompt_template_id=conversation.prompt_template_id,
                    user_info=conversation.user_info,
                    title=conversation.title,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at,
                    message_count=len(conversation.messages),
                )
                for conversation in conversations
            ]

    def get_conversation_by_id(self, conversation_id: int) -> ConversationResponse:
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                raise RuntimeError("Conversation not found")
            return ConversationResponse(
                id=conversation.id,
                character_id=conversation.character_id,
                prompt_template_id=conversation.prompt_template_id,
                user_info=conversation.user_info,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )

    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> list[MessageResponse]:
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                raise RuntimeError("Conversation not found")

            messages = conversation.messages[-limit:]
            return [
                MessageResponse(
                    id=index + 1,
                    conversation_id=conversation.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for index, message in enumerate(messages)
            ]

    def update_conversation(
        self,
        conversation_id: int,
        conversation_data: ConversationUpdate,
    ) -> ConversationResponse:
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                raise RuntimeError("Conversation not found")

            if conversation_data.title is not None:
                conversation.title = conversation_data.title
            if conversation_data.user_info is not None:
                conversation.user_info = conversation_data.user_info
            conversation.updated_at = datetime.now(timezone.utc).isoformat()
            self._save()
            return self.get_conversation_by_id(conversation_id)

    def delete_conversation(self, conversation_id: int) -> None:
        with self._lock:
            if conversation_id not in self._conversations:
                raise RuntimeError("Conversation not found")
            del self._conversations[conversation_id]
            self._save()

    def _resolve_context(self, request: ChatRequest) -> tuple[Character, PromptTemplate]:
        chat_settings = self._settings_service.get_chat_settings()
        character_id = request.character_id or chat_settings.default_character_id
        prompt_template_id = request.prompt_template_id or chat_settings.default_prompt_template_id

        if character_id is None:
            characters = self._catalog_service.list_characters()
            character_id = characters[0].id if characters else None

        if prompt_template_id is None:
            templates = self._catalog_service.list_prompt_templates()
            prompt_template_id = templates[0].id if templates else None

        if character_id is None or prompt_template_id is None:
            raise RuntimeError("characterId and promptTemplateId are required")

        character = next(
            (item for item in self._catalog_service.list_characters() if item.id == character_id),
            None,
        )
        prompt_template = next(
            (
                item
                for item in self._catalog_service.list_prompt_templates()
                if item.id == prompt_template_id
            ),
            None,
        )

        if character is None:
            raise RuntimeError("Character not found")
        if prompt_template is None:
            raise RuntimeError("Prompt template not found")

        return character, prompt_template

    def _build_prompt(
        self,
        request: ChatRequest,
        character: Character,
        prompt_template: PromptTemplate,
    ) -> tuple[str, str]:
        user_name = request.user_name or ""
        character_name = character.name
        system_message = self._substitute(prompt_template.content, user_name, character_name)
        character_prompt = self._substitute(character.prompt_content, user_name, character_name)
        user_info = self._substitute(request.user_info or "", user_name, character_name)

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

        with self._lock:
            conversation = self._conversations.get(request.conversation_id)
            if conversation is None or not conversation.messages:
                return "[Start a new chat]"

            formatted: list[str] = []
            for message in conversation.messages[-20:]:
                if message.role == "system":
                    continue
                role = "user" if message.role == "user" else "model"
                formatted.append(
                    json.dumps(
                        {
                            "role": role,
                            "timestamp": message.created_at,
                            "parts": [{"text": message.content}],
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
        character_id: int,
        prompt_template_id: int,
    ) -> int:
        with self._lock:
            if request.conversation_id and request.conversation_id in self._conversations:
                conversation = self._conversations[request.conversation_id]
            else:
                conversation_id = max(self._conversations.keys(), default=0) + 1
                conversation = ConversationRecord(
                    id=conversation_id,
                    character_id=character_id,
                    prompt_template_id=prompt_template_id,
                    title=request.title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    user_info=request.user_info,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    updated_at=datetime.now(timezone.utc).isoformat(),
                    messages=[],
                )
                self._conversations[conversation_id] = conversation

            timestamp = datetime.now(timezone.utc).isoformat()
            if request.role == "user":
                conversation.messages.append(
                    ConversationMessage(role="user", content=request.message, created_at=timestamp)
                )
            conversation.messages.append(
                ConversationMessage(role="assistant", content=response_text, created_at=timestamp)
            )
            conversation.updated_at = timestamp
            self._save()
            return conversation.id

    def _resolve_workspace_dir(self) -> Path:
        settings = get_settings()
        target = settings.data_dir_path / "workspace"
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

    def _load(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._save()
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._conversations = {}
            self._save()
            return

        conversations: dict[int, ConversationRecord] = {}
        for raw in payload.get("conversations", []):
            messages = [
                ConversationMessage(
                    role=item["role"],
                    content=item["content"],
                    created_at=item["createdAt"],
                )
                for item in raw.get("messages", [])
            ]
            record = ConversationRecord(
                id=raw["id"],
                character_id=raw["characterId"],
                prompt_template_id=raw["promptTemplateId"],
                title=raw["title"],
                user_info=raw.get("userInfo"),
                created_at=raw.get("createdAt", datetime.now(timezone.utc).isoformat()),
                updated_at=raw.get("updatedAt", datetime.now(timezone.utc).isoformat()),
                messages=messages,
            )
            conversations[record.id] = record
        self._conversations = conversations

    def _save(self) -> None:
        payload = {
            "conversations": [
                {
                    "id": record.id,
                    "characterId": record.character_id,
                    "promptTemplateId": record.prompt_template_id,
                    "title": record.title,
                    "userInfo": record.user_info,
                    "createdAt": record.created_at,
                    "updatedAt": record.updated_at,
                    "messages": [
                        {
                            "role": message.role,
                            "content": message.content,
                            "createdAt": message.created_at,
                        }
                        for message in record.messages
                    ],
                }
                for record in self._conversations.values()
            ]
        }
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


_settings = get_settings()
_service = ChatService(
    _settings.data_dir_path / "chat.json",
    get_settings_service(),
    get_ai_catalog_service(),
    get_command_template_service(),
)


def get_chat_service() -> ChatService:
    return _service
