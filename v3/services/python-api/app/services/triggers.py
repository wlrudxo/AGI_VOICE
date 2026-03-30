import asyncio
import json
import re
import threading
import time
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.chat import ChatRequest
from app.services.action_service import ActionService, get_action_service
from app.services.carmaker import CarMakerService, get_carmaker_service
from app.services.chat import ChatService, get_chat_service
from app.services.settings import SettingsService, get_settings_service
from app.schemas.triggers import (
    CreateTriggerRequest,
    Trigger,
    TriggerChatEvent,
    TriggerCollection,
    UpdateTriggerRequest,
    utc_now,
)


class TriggerService:
    def __init__(
        self,
        storage_path: Path,
        carmaker_service: CarMakerService,
        action_service: ActionService,
        chat_service: ChatService,
        settings_service: SettingsService,
    ) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._carmaker_service = carmaker_service
        self._action_service = action_service
        self._chat_service = chat_service
        self._settings_service = settings_service
        self._triggers: list[Trigger] = []
        self._log_messages: list[str] = []
        self._monitoring_active = False
        self._monitor_thread: threading.Thread | None = None
        self._cooldowns: dict[int, float] = {}
        self._blocked_until = 0.0
        self._is_executing = False
        self._cancel_event = threading.Event()
        self._events: list[TriggerChatEvent] = []
        self._next_event_id = 1
        self._load()

    def list_triggers(self) -> list[Trigger]:
        with self._lock:
            return [trigger.model_copy(deep=True) for trigger in self._triggers]

    def get_trigger(self, trigger_id: int) -> Trigger | None:
        with self._lock:
            trigger = self._find_trigger(trigger_id)
            return trigger.model_copy(deep=True) if trigger else None

    def create_trigger(self, request: CreateTriggerRequest) -> Trigger:
        with self._lock:
            trigger = Trigger(
                id=self._next_id(),
                name=request.name,
                expression=request.expression,
                message=request.message,
                conversation_id=request.conversation_id,
                use_rule_control=request.use_rule_control,
                debug_action=request.debug_action,
                cooldown=request.cooldown,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            self._triggers.append(trigger)
            self._save()
            return trigger.model_copy(deep=True)

    def update_trigger(self, trigger_id: int, request: UpdateTriggerRequest) -> Trigger:
        with self._lock:
            index, existing = self._require_trigger(trigger_id)
            updated = Trigger(
                id=existing.id,
                name=request.name,
                is_active=existing.is_active,
                expression=request.expression,
                message=request.message,
                conversation_id=request.conversation_id,
                use_rule_control=request.use_rule_control,
                debug_action=request.debug_action,
                cooldown=request.cooldown,
                created_at=existing.created_at,
                updated_at=utc_now(),
            )
            self._triggers[index] = updated
            self._save()
            return updated.model_copy(deep=True)

    def delete_trigger(self, trigger_id: int) -> None:
        with self._lock:
            index, _ = self._require_trigger(trigger_id)
            self._triggers.pop(index)
            self._save()

    def toggle_trigger(self, trigger_id: int) -> Trigger:
        with self._lock:
            index, existing = self._require_trigger(trigger_id)
            updated = existing.model_copy(
                update={
                    "is_active": not existing.is_active,
                    "updated_at": utc_now(),
                }
            )
            self._triggers[index] = updated
            self._save()
            return updated.model_copy(deep=True)

    def toggle_rule_control(self, trigger_id: int) -> Trigger:
        with self._lock:
            index, existing = self._require_trigger(trigger_id)
            updated = existing.model_copy(
                update={
                    "use_rule_control": not existing.use_rule_control,
                    "updated_at": utc_now(),
                }
            )
            self._triggers[index] = updated
            self._save()
            return updated.model_copy(deep=True)

    def is_monitoring_active(self) -> bool:
        with self._lock:
            return self._monitoring_active

    def set_monitoring_state(self, active: bool) -> bool:
        return self._set_monitoring_state(active, reset_cooldowns=active)

    def _set_monitoring_state(self, active: bool, reset_cooldowns: bool) -> bool:
        with self._lock:
            if active == self._monitoring_active:
                return self._monitoring_active

            self._monitoring_active = active
            if active:
                if reset_cooldowns:
                    self._cooldowns.clear()
                self._add_log("✓ Started trigger monitoring (10Hz backend)")
                self._ensure_monitor_thread()
            else:
                self._add_log("✓ Stopped trigger monitoring")
            return self._monitoring_active

    def get_logs(self) -> list[str]:
        with self._lock:
            return list(self._log_messages)

    def clear_logs(self) -> list[str]:
        with self._lock:
            self._log_messages.clear()
            return []

    def cancel_active_execution(self) -> bool:
        with self._lock:
            if not self._is_executing:
                return False
            self._cancel_event.set()
            self._add_log("🛑 Reset Control requested: cancelling active trigger execution")
            return True

    def reset_runtime_state(self) -> dict[str, bool]:
        with self._lock:
            was_executing = self._is_executing
            self._cancel_event.set()
            self._monitoring_active = False
            self._cooldowns.clear()
            self._blocked_until = 0.0
            self._events.clear()
            self._next_event_id = 1
            self._add_log("🛑 Reset Control: trigger monitoring stopped and runtime state cleared")
            return {
                "was_executing": was_executing,
                "monitoring_active": self._monitoring_active,
            }

    def get_events(self, since_id: int = 0) -> list[TriggerChatEvent]:
        with self._lock:
            return [
                event.model_copy(deep=True)
                for event in self._events
                if event.id > since_id
            ]

    def _find_trigger(self, trigger_id: int) -> Trigger | None:
        return next((trigger for trigger in self._triggers if trigger.id == trigger_id), None)

    def _require_trigger(self, trigger_id: int) -> tuple[int, Trigger]:
        for index, trigger in enumerate(self._triggers):
            if trigger.id == trigger_id:
                return index, trigger
        raise RuntimeError(f"Trigger with id {trigger_id} not found")

    def _next_id(self) -> int:
        return max((trigger.id for trigger in self._triggers), default=0) + 1

    def _load(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._save()
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._triggers = []
            self._save()
            return

        try:
            collection = TriggerCollection.model_validate(payload)
        except ValidationError:
            self._triggers = []
            self._save()
            return

        self._triggers = list(collection.triggers)

    def _save(self) -> None:
        payload = TriggerCollection(triggers=self._triggers)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            payload.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )

    def _ensure_monitor_thread(self) -> None:
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="agi-voice-v3-trigger-monitor",
            daemon=True,
        )
        self._monitor_thread.start()

    def _monitor_loop(self) -> None:
        while True:
            with self._lock:
                active = self._monitoring_active

            if not active:
                break

            try:
                self._tick_monitoring()
            except Exception as exc:
                self._add_log(f"✗ Trigger runtime error: {exc}")

            time.sleep(0.1)

    def _tick_monitoring(self) -> None:
        with self._lock:
            if not self._monitoring_active or self._is_executing:
                return

        if not self._carmaker_service.is_monitoring_active():
            return

        telemetry = self._carmaker_service.get_telemetry()
        vehicle_data = telemetry.raw_data
        if not vehicle_data:
            return

        active_triggers = self.list_triggers()
        now = time.time()

        with self._lock:
            if now < self._blocked_until:
                return

        for trigger in active_triggers:
            if not trigger.is_active:
                continue

            next_allowed = self._cooldowns.get(trigger.id, 0.0)
            if now < next_allowed:
                continue

            if not self._evaluate_expression(trigger.expression, vehicle_data):
                continue

            with self._lock:
                if not self._monitoring_active or self._is_executing:
                    return
                self._is_executing = True
                blocked_until = now + (trigger.cooldown / 1000.0)
                self._cooldowns[trigger.id] = blocked_until
                self._blocked_until = blocked_until
            self._add_log(f"⚡ Trigger activated: {trigger.name}")

            snapshot = ", ".join(
                f"{key}={value:.4f}"
                for key, value in sorted(vehicle_data.items())
            )
            self._add_log(f"  Vehicle data: {snapshot}")
            self._execute_trigger(trigger, vehicle_data)
            return

    def _execute_trigger(self, trigger: Trigger, vehicle_data: dict[str, float]) -> None:
        self._cancel_event.clear()
        was_monitoring = False
        try:
            self._add_log("  → Pausing simulation (time scale = 0.001x)")
            was_monitoring = self._carmaker_service.is_monitoring_active()
            if was_monitoring:
                self._set_monitoring_state(False, reset_cooldowns=False)
                self._add_log("  → Monitoring paused (prevent timeout in low-speed mode)")
            self._carmaker_service.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")

            if trigger.use_rule_control and trigger.debug_action.strip():
                self._add_log("  → Rule mode: waiting 1 second")
                self._sleep_with_cancel(1.0)
                self._add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
                if was_monitoring:
                    self._set_monitoring_state(True, reset_cooldowns=False)
                    self._add_log("  → Monitoring resumed")
                self._add_log("  → Rule mode: executing backend rule action")
                self._action_service.execute_command_sequence(
                    trigger.debug_action,
                    cancel_event=self._cancel_event,
                    logger=self._add_log,
                )
            else:
                self._add_log("  → LLM mode: requesting AI response")
                llm_response = asyncio.run(self._request_llm(trigger, vehicle_data))
                self._add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
                if was_monitoring:
                    self._set_monitoring_state(True, reset_cooldowns=False)
                    self._add_log("  → Monitoring resumed")
                if self._cancel_event.is_set():
                    self._add_log("  → Trigger execution cancelled after AI response wait")
                elif llm_response:
                    self._add_log("  → Parsing LLM response and executing commands")
                    self._action_service.execute_command_sequence(
                        llm_response,
                        cancel_event=self._cancel_event,
                        logger=self._add_log,
                    )
            self._add_log("  ✓ Trigger action sequence completed")
        except Exception as exc:
            self._add_log(f"  ✗ Trigger action failed: {exc}")
            try:
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
            except Exception:
                pass
            if was_monitoring:
                try:
                    self._set_monitoring_state(True, reset_cooldowns=False)
                    self._add_log("  → Monitoring resumed")
                except Exception:
                    pass
        finally:
            self._is_executing = False
            self._cancel_event.clear()

    def _evaluate_expression(self, expression: str, vehicle_data: dict[str, float]) -> bool:
        if not expression.strip():
            return False

        normalized = expression.replace("&&", " and ").replace("||", " or ")
        token_pattern = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*\b")
        reserved = {"and", "or", "not", "abs", "sqrt", "pow", "min", "max", "True", "False"}

        def replace_token(match: re.Match[str]) -> str:
            token = match.group(0)
            if token in reserved:
                return token
            return f'_get("{token}")'

        python_expr = token_pattern.sub(replace_token, normalized)
        safe_globals = {
            "__builtins__": {},
            "abs": abs,
            "sqrt": math.sqrt,
            "pow": pow,
            "min": min,
            "max": max,
        }
        safe_locals = {
            "_get": lambda key: vehicle_data.get(key, 0.0),
        }

        try:
            result = eval(python_expr, safe_globals, safe_locals)
        except Exception as exc:
            self._add_log(f"✗ Trigger evaluation failed: {exc}")
            return False

        return bool(result)

    async def _request_llm(self, trigger: Trigger, vehicle_data: dict[str, float]) -> str | None:
        try:
            system_context = self._build_system_context(trigger, vehicle_data)
            self._add_multiline_log(
                f"  === LLM INPUT BEGIN ({trigger.name}) ===",
                system_context,
                f"  === LLM INPUT END ({trigger.name}) ===",
            )
            self._print_debug_block(
                "Trigger AI Input",
                system_context,
                metadata={
                    "trigger_id": trigger.id,
                    "trigger_name": trigger.name,
                    "conversation_id": trigger.conversation_id,
                },
            )
            self._add_event("system", trigger.name, system_context)
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
            response = await self._chat_service.chat(request, abort_event=self._cancel_event)
            if not response.responses:
                self._add_log("  ⚠ LLM returned no response")
                return None

            llm_response = response.responses[0]
            self._add_log(f"  ✓ LLM response received ({len(llm_response)} chars)")
            self._add_multiline_log(
                f"  === LLM OUTPUT BEGIN ({trigger.name}) ===",
                llm_response,
                f"  === LLM OUTPUT END ({trigger.name}) ===",
            )
            self._print_debug_block(
                "Trigger AI Output",
                llm_response,
                metadata={
                    "trigger_id": trigger.id,
                    "trigger_name": trigger.name,
                },
            )
            self._add_event("llm_response", trigger.name, llm_response)
            return llm_response
        except Exception as exc:
            self._add_log(f"  ✗ LLM request failed: {exc}")
            self._add_event("error", trigger.name, f"LLM 요청 실패: {exc}")
            return None

    def _sleep_with_cancel(self, seconds: float) -> None:
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self._cancel_event.is_set():
                raise RuntimeError("Trigger execution cancelled")
            time.sleep(0.05)

    def _build_system_context(self, trigger: Trigger, vehicle_data: dict[str, float]) -> str:
        data_snapshot = "\n".join(
            f"{key}: {value:.4f}"
            for key, value in sorted(vehicle_data.items())
        )
        return (
            "## Current Vehicle Data:\n"
            f"{data_snapshot}\n\n"
            "## Trigger Message:\n"
            f"{trigger.message}"
        )

    def _add_log(self, message: str) -> None:
        timestamp = time.strftime("%I:%M:%S %p")
        self._log_messages = [*self._log_messages, f"[{timestamp}] {message}"][-100:]

    def _add_multiline_log(self, begin: str, content: str, end: str) -> None:
        self._add_log(begin)
        for line in content.splitlines():
            self._add_log(f"    {line}")
        self._add_log(end)

    def _add_event(self, event_type: str, trigger_name: str, content: str) -> None:
        with self._lock:
            event = TriggerChatEvent(
                id=self._next_event_id,
                type=event_type,
                trigger_name=trigger_name,
                content=content,
                created_at=utc_now(),
            )
            self._next_event_id += 1
            self._events = [*self._events, event][-200:]

    def _print_debug_block(
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


_settings = get_settings()
_service = TriggerService(
    _settings.data_dir_path / "triggers.json",
    get_carmaker_service(),
    get_action_service(),
    get_chat_service(),
    get_settings_service(),
)


def get_trigger_service() -> TriggerService:
    return _service
