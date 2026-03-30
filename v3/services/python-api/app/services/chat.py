import asyncio
import codecs
import json
import os
import shutil
import subprocess
import textwrap
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from app.core.config import get_settings
from app.schemas.ai_catalog import PromptTemplate
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversations import (
    ConversationCreate,
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

    async def chat(
        self,
        request: ChatRequest,
        abort_event: threading.Event | None = None,
    ) -> ChatResponse:
        conversation_id, prompt_template = self._resolve_chat_session(request)
        workspace_dir = self._resolve_workspace_dir()
        self._remove_legacy_claude_md(workspace_dir)
        request_input = request.system_context.strip() if request.system_context else request.message.strip()
        prompt = self._build_prompt(request, prompt_template)
        self._log_debug_block(
            "Request Input",
            request_input,
            metadata={
                "conversation_id": conversation_id,
                "prompt_template_id": prompt_template.id,
                "model": request.model,
                "role": request.role,
                "no_save": request.no_save,
                "exclude_history": request.exclude_history,
            },
        )
        self._log_debug_block(
            "LLM Input",
            prompt,
            metadata={
                "conversation_id": conversation_id,
                "prompt_template_id": prompt_template.id,
                "model": request.model,
                "role": request.role,
                "no_save": request.no_save,
                "exclude_history": request.exclude_history,
            },
        )
        response_text = await self._run_claude(prompt, request.model, workspace_dir, abort_event)
        self._log_debug_block("LLM Output", response_text)

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
            prompt_template.id,
        )
        return ChatResponse(
            conversation_id=conversation_id,
            responses=[response_text],
            actions=[],
        )

    async def generate_trigger_response(
        self,
        system_context: str,
        abort_event: threading.Event | None = None,
    ) -> str:
        trigger_ai = self._settings_service.get_trigger_ai_settings()
        chat_settings = self._settings_service.get_chat_settings()
        request = ChatRequest(
            message="Trigger activated. Please provide vehicle control response.",
            system_context=system_context,
            role="system",
            exclude_history=trigger_ai.exclude_history,
            no_save=trigger_ai.exclude_history,
            model=trigger_ai.model or chat_settings.default_claude_model,
            prompt_template_id=(
                trigger_ai.prompt_template_id or chat_settings.default_prompt_template_id
            ),
        )
        response = await self.chat(request, abort_event=abort_event)
        if not response.responses:
            raise RuntimeError("LLM returned no response")
        return response.responses[0]

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
                    prompt_template_id=row["prompt_template_id"],
                    title=row["title"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    message_count=row["message_count"],
                )
                for row in conversations
            ]

    def create_conversation(self, conversation_data: ConversationCreate) -> ConversationResponse:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            now = utc_now_iso()
            cursor = conn.execute(
                """
                INSERT INTO conversations (
                    prompt_template_id, title, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    conversation_data.prompt_template_id,
                    conversation_data.title,
                    now,
                    now,
                ),
            )
            conn.commit()
            conversation_id = int(cursor.lastrowid)
            return self.get_conversation_by_id(conversation_id)

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
                prompt_template_id=row["prompt_template_id"],
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
            if conversation_data.title is not None:
                next_title = conversation_data.title

            conn.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
                """,
                (next_title, utc_now_iso(), conversation_id),
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
    ) -> tuple[int | None, PromptTemplate]:
        # V2 parity:
        # - existing conversation always uses the stored prompt template
        # - new conversation and no-save mode require explicit request template id
        conversation_id: int | None = None
        prompt_template_id: int | None = None

        if not request.no_save and request.conversation_id is not None:
            with self._lock, self._db.with_lock(), self._db.connect() as conn:
                row = conn.execute(
                    "SELECT id, prompt_template_id FROM conversations WHERE id = ?",
                    (request.conversation_id,),
                ).fetchone()
            if row is None:
                raise RuntimeError("Conversation not found")
            conversation_id = int(row["id"])
            prompt_template_id = int(row["prompt_template_id"])
        else:
            if request.prompt_template_id is None:
                raise RuntimeError("promptTemplateId is required for new conversation")
            prompt_template_id = request.prompt_template_id

        prompt_template = next(
            (item for item in self._catalog_service.list_prompt_templates() if item.id == prompt_template_id),
            None,
        )

        if prompt_template is None:
            raise RuntimeError("Prompt template not found")

        return conversation_id, prompt_template

    def _build_prompt(
        self,
        request: ChatRequest,
        prompt_template: PromptTemplate,
    ) -> str:
        system_message = prompt_template.content

        command_info_list = [
            item.content for item in self._command_template_service.list_templates(is_active=1)
        ]
        history_block = self._format_history(request)
        current_input = request.system_context.strip() if request.system_context else request.message.strip()
        full_message = textwrap.dedent(
            f"""
            ## System Message

            {system_message.strip()}

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
            """
        ).strip()

        return full_message

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
                timestamp = self._format_prompt_timestamp(row["created_at"])
                formatted.append(
                    json.dumps(
                        {
                            "role": role,
                            "timestamp": timestamp,
                            "parts": [{"text": row["content"]}],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            return ",\n".join(formatted) if formatted else "[Start a new chat]"

    def _format_prompt_timestamp(self, raw_timestamp: str | None) -> str | None:
        if not raw_timestamp:
            return None

        try:
            parsed = raw_timestamp.strip()
            if parsed.endswith("Z"):
                dt = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
            elif "T" in parsed or "+" in parsed:
                dt = datetime.fromisoformat(parsed)
            else:
                dt = datetime.strptime(parsed, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return raw_timestamp

        kst = dt.astimezone(timezone.utc) + timedelta(hours=9)
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][kst.weekday()]
        return f"{kst.year:04d}-{kst.month:02d}-{kst.day:02d} {weekday} {kst.hour:02d}:{kst.minute:02d}"

    def _persist_chat(
        self,
        request: ChatRequest,
        response_text: str,
        conversation_id: int | None,
        prompt_template_id: int,
    ) -> int:
        with self._lock, self._db.with_lock(), self._db.connect() as conn:
            now = utc_now_iso()
            if conversation_id is not None:
                conn.execute(
                    """
                    UPDATE conversations SET updated_at = ? WHERE id = ?
                    """,
                    (now, conversation_id),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO conversations (
                        prompt_template_id, title, created_at, updated_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        prompt_template_id,
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

    def _remove_legacy_claude_md(self, workspace_dir: Path) -> None:
        legacy_path = workspace_dir / "CLAUDE.md"
        if legacy_path.exists():
            legacy_path.unlink()

    async def _run_claude(
        self,
        prompt: str,
        model: str,
        workspace_dir: Path,
        abort_event: threading.Event | None = None,
    ) -> str:
        settings = get_settings()
        timeout_seconds = max(1, settings.claude_timeout_seconds)
        claude_bin = self._resolve_claude_cli()
        if not claude_bin:
            raise RuntimeError("Claude CLI not found")

        args = [
            "-p",
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
            "--model",
            model,
            "--disallowedTools",
            "TodoWrite,Task,Bash,WebSearch,WebFetch",
        ]
        command = self._build_claude_command(claude_bin, args)
        self._print_runtime_status(
            f"Claude request started (model={model}, timeout={timeout_seconds}s)"
        )
        if os.name == "nt":
            returncode, stdout_text, stderr_text = await asyncio.to_thread(
                self._run_claude_blocking_stream,
                command,
                prompt,
                workspace_dir,
                abort_event,
                timeout_seconds,
            )
        else:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(workspace_dir),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
            )
            assert process.stdin is not None
            process.stdin.write((prompt + "\n").encode("utf-8"))
            await process.stdin.drain()
            process.stdin.close()

            started_at = time.monotonic()
            next_status_at = started_at + 5.0
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []
            full_response = ""
            stdout_decoder = codecs.getincrementaldecoder("utf-8")("replace")
            stderr_decoder = codecs.getincrementaldecoder("utf-8")("replace")
            stdout_buffer = ""

            while True:
                if abort_event is not None and abort_event.is_set():
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                    raise RuntimeError("Trigger execution cancelled")

                elapsed = time.monotonic() - started_at
                if process.returncode is None and elapsed >= timeout_seconds:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                    raise RuntimeError(f"Claude CLI timed out after {timeout_seconds}s")

                if elapsed >= next_status_at - started_at:
                    self._print_runtime_status(
                        f"Claude request still running ({int(elapsed)}s elapsed)"
                    )
                    next_status_at += 5.0

                if process.stdout is not None:
                    try:
                        chunk = await asyncio.wait_for(process.stdout.read(4096), timeout=0.1)
                    except asyncio.TimeoutError:
                        chunk = b""
                    if chunk:
                        decoded = stdout_decoder.decode(chunk)
                        stdout_text_piece, stdout_buffer, full_response = self._consume_stream_text(
                            decoded,
                            stdout_buffer,
                            full_response,
                        )
                        if stdout_text_piece:
                            stdout_lines.append(stdout_text_piece)
                        continue

                if process.returncode is not None:
                    break

            remaining_stdout = stdout_decoder.decode(b"", final=True)
            stdout_text_piece, stdout_buffer, full_response = self._consume_stream_text(
                remaining_stdout,
                stdout_buffer,
                full_response,
            )
            if stdout_text_piece:
                stdout_lines.append(stdout_text_piece)
            if stdout_buffer.strip():
                stdout_lines.append(stdout_buffer)

            if process.stderr is not None:
                stderr_bytes = await process.stderr.read()
                stderr_text = stderr_decoder.decode(stderr_bytes, final=True)
                if stderr_text:
                    stderr_lines.append(stderr_text)

            returncode = process.returncode or 0
            stdout_text = "".join(stdout_lines)
            stderr_text = "".join(stderr_lines)
        if returncode != 0:
            error_text = stderr_text.strip()
            raise RuntimeError(error_text or f"Claude CLI exited with {returncode}")

        response_text = full_response if os.name != "nt" else self._extract_stream_json(stdout_text)
        if not response_text.strip():
            raise RuntimeError("Claude CLI returned an empty response")
        self._print_runtime_status("Claude request completed")
        return response_text

    def _run_claude_blocking_stream(
        self,
        command: list[str],
        prompt: str,
        workspace_dir: Path,
        abort_event: threading.Event | None = None,
        timeout_seconds: int = 90,
    ) -> tuple[int, str, str]:
        process = subprocess.Popen(
            command,
            cwd=str(workspace_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
        )
        assert process.stdin is not None
        process.stdin.write((prompt + "\n").encode("utf-8"))
        process.stdin.close()

        started_at = time.monotonic()
        next_status_at = started_at + 5.0
        stdout_lines: list[str] = []
        full_response = ""
        assert process.stdout is not None
        while True:
            if abort_event is not None and abort_event.is_set():
                process.terminate()
                try:
                    _, stderr = process.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    _, stderr = process.communicate()
                stderr_text = stderr.decode("utf-8", errors="replace")
                return 130, "".join(stdout_lines), stderr_text or "Trigger execution cancelled"

            elapsed = time.monotonic() - started_at
            if elapsed >= timeout_seconds:
                process.terminate()
                try:
                    _, stderr = process.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    _, stderr = process.communicate()
                stderr_text = stderr.decode("utf-8", errors="replace")
                return 124, "".join(stdout_lines), stderr_text or f"Claude CLI timed out after {timeout_seconds}s"

            if process.poll() is not None:
                break

            line = process.stdout.readline()
            if line:
                decoded = line.decode("utf-8", errors="replace")
                stdout_lines.append(decoded)
                continue

            if elapsed >= next_status_at - started_at:
                self._print_runtime_status(
                    f"Claude request still running ({int(elapsed)}s elapsed)"
                )
                next_status_at += 5.0

            time.sleep(0.1)

        remaining_stdout, stderr = process.communicate()
        if remaining_stdout:
            stdout_lines.append(remaining_stdout.decode("utf-8", errors="replace"))
        stderr_text = stderr.decode("utf-8", errors="replace")
        return process.returncode or 0, "".join(stdout_lines), stderr_text

    def _consume_stream_text(
        self,
        decoded_chunk: str,
        buffer: str,
        full_response: str,
    ) -> tuple[str, str, str]:
        if not decoded_chunk:
            return "", buffer, full_response

        combined = buffer + decoded_chunk
        lines = combined.splitlines(keepends=True)
        next_buffer = ""
        if lines and not lines[-1].endswith("\n"):
            next_buffer = lines.pop()

        text_piece = "".join(lines)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
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

        return text_piece, next_buffer, full_response

    def _resolve_claude_cli(self) -> str | None:
        env_path = os.getenv("AGI_VOICE_CLAUDE_BIN")
        if env_path and Path(env_path).exists():
            return env_path

        direct = shutil.which("claude")
        if direct:
            return direct

        if os.name != "nt":
            return None

        for candidate in self._iter_windows_claude_candidates():
            if candidate.is_file():
                return str(candidate)
        return None

    def _iter_windows_claude_candidates(self) -> Iterable[Path]:
        user_profile = os.getenv("USERPROFILE")
        if user_profile:
            yield Path(user_profile) / ".local" / "bin" / "claude.exe"

        appdata = os.getenv("APPDATA")
        if appdata:
            # npm global install location
            yield Path(appdata) / "npm" / "claude.cmd"
            yield Path(appdata) / "npm" / "claude.exe"

            base_dir = Path(appdata) / "Claude" / "claude-code"
            if base_dir.is_dir():
                version_dirs: list[tuple[list[int], Path]] = []
                for child in base_dir.iterdir():
                    if not child.is_dir():
                        continue
                    version = self._parse_version(child.name)
                    if version is None:
                        continue
                    version_dirs.append((version, child))

                for _, version_dir in sorted(version_dirs, reverse=True):
                    yield version_dir / "claude.exe"
                    yield version_dir / "claude.cmd"

    def _parse_version(self, value: str) -> list[int] | None:
        parts: list[int] = []
        for part in value.split("."):
            if not part.isdigit():
                return None
            parts.append(int(part))
        return parts or None

    def _build_claude_command(self, claude_bin: str, args: list[str]) -> list[str]:
        suffix = Path(claude_bin).suffix.lower()
        if suffix in {".cmd", ".bat"}:
            return ["cmd.exe", "/C", claude_bin, *args]
        return [claude_bin, *args]

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

    def _log_debug_block(
        self,
        title: str,
        content: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        config_settings = get_settings()
        app_settings = self._settings_service.get_app_settings()
        if not (config_settings.debug_chat_logs or app_settings.debug_chat_logs):
            return

        print(f"=== {title} ===")
        if metadata:
            print(json.dumps(metadata, ensure_ascii=False, indent=2))
        print(content)
        print(f"=== End {title} ===")

    def _print_runtime_status(self, message: str) -> None:
        config_settings = get_settings()
        app_settings = self._settings_service.get_app_settings()
        if not (config_settings.debug_chat_logs or app_settings.debug_chat_logs):
            return
        print(f"[LLM] {message}")


_service = ChatService(
    get_ai_chat_db(),
    get_settings_service(),
    get_ai_catalog_service(),
    get_command_template_service(),
)


def get_chat_service() -> ChatService:
    return _service
