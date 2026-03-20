import asyncio
import json
import math
import re
import threading
import time
from pathlib import Path
from dataclasses import dataclass

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.chat import ChatRequest
from app.services.carmaker import CarMakerService, get_carmaker_service
from app.services.chat import ChatService, get_chat_service
from app.services.settings import SettingsService, get_settings_service
from app.schemas.triggers import (
    CreateTriggerRequest,
    Trigger,
    TriggerCollection,
    UpdateTriggerRequest,
    utc_now,
)


@dataclass
class VehicleCommand:
    variable: str
    value: float
    duration: int
    mode: str


@dataclass
class WaitCommand:
    milliseconds: int


@dataclass
class WaitUntilCommand:
    condition: str
    timeout: int = 30000


class TriggerService:
    def __init__(
        self,
        storage_path: Path,
        carmaker_service: CarMakerService,
        chat_service: ChatService,
        settings_service: SettingsService,
    ) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._carmaker_service = carmaker_service
        self._chat_service = chat_service
        self._settings_service = settings_service
        self._triggers: list[Trigger] = []
        self._log_messages: list[str] = []
        self._monitoring_active = False
        self._monitor_thread: threading.Thread | None = None
        self._cooldowns: dict[int, float] = {}
        self._is_executing = False
        self._load()

    def list_triggers(self) -> list[Trigger]:
        with self._lock:
            return [trigger.model_copy(deep=True) for trigger in self._triggers]

    def get_all(self) -> list[Trigger]:
        return self.list_triggers()

    def get_trigger(self, trigger_id: int) -> Trigger | None:
        with self._lock:
            trigger = self._find_trigger(trigger_id)
            return trigger.model_copy(deep=True) if trigger else None

    def get_by_id(self, trigger_id: int) -> Trigger:
        trigger = self.get_trigger(trigger_id)
        if trigger is None:
            raise RuntimeError(f"Trigger with id {trigger_id} not found")
        return trigger

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

    def create(self, request: CreateTriggerRequest) -> Trigger:
        return self.create_trigger(request)

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

    def update(self, trigger_id: int, request: UpdateTriggerRequest) -> Trigger:
        return self.update_trigger(trigger_id, request)

    def delete_trigger(self, trigger_id: int) -> None:
        with self._lock:
            index, _ = self._require_trigger(trigger_id)
            self._triggers.pop(index)
            self._save()

    def delete(self, trigger_id: int) -> None:
        self.delete_trigger(trigger_id)

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

    def toggle_active(self, trigger_id: int) -> Trigger:
        return self.toggle_trigger(trigger_id)

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
        with self._lock:
            if active == self._monitoring_active:
                return self._monitoring_active

            self._monitoring_active = active
            if active:
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
        if not self._carmaker_service.is_monitoring_active():
            return

        if self._is_executing:
            return

        telemetry = self._carmaker_service.get_telemetry()
        vehicle_data = telemetry.raw_data
        if not vehicle_data:
            return

        active_triggers = self.list_triggers()
        now = time.time()

        for trigger in active_triggers:
            if not trigger.is_active:
                continue

            next_allowed = self._cooldowns.get(trigger.id, 0.0)
            if now < next_allowed:
                continue

            if not self._evaluate_expression(trigger.expression, vehicle_data):
                continue

            self._cooldowns[trigger.id] = now + (trigger.cooldown / 1000.0)
            self._add_log(f"⚡ Trigger activated: {trigger.name}")

            snapshot = ", ".join(
                f"{key}={value:.4f}"
                for key, value in sorted(vehicle_data.items())
            )
            self._add_log(f"  Vehicle data: {snapshot}")
            self._execute_trigger(trigger, vehicle_data)

    def _execute_trigger(self, trigger: Trigger, vehicle_data: dict[str, float]) -> None:
        self._is_executing = True
        try:
            self._add_log("  → Pausing simulation (time scale = 0.001x)")
            self._carmaker_service.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")

            if trigger.use_rule_control and trigger.debug_action.strip():
                self._add_log("  → Rule mode: waiting 1 second")
                time.sleep(1.0)
                self._add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 1000 Abs")
                self._add_log("  → Rule mode: executing backend rule action")
                self._execute_command_sequence(trigger.debug_action)
            else:
                self._add_log("  → LLM mode: requesting AI response")
                llm_response = asyncio.run(self._request_llm(trigger, vehicle_data))
                self._add_log("  → Resuming simulation (time scale = 1.0x)")
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 1000 Abs")
                if llm_response:
                    self._add_log("  → Parsing LLM response and executing commands")
                    self._execute_command_sequence(llm_response)
            self._add_log("  ✓ Trigger action sequence completed")
        except Exception as exc:
            self._add_log(f"  ✗ Trigger action failed: {exc}")
            try:
                self._carmaker_service.execute_command("DVAWrite SC.TAccel 1.0 1000 Abs")
            except Exception:
                pass
        finally:
            self._is_executing = False

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
            trigger_ai = self._settings_service.get_trigger_ai_settings()
            chat_settings = self._settings_service.get_chat_settings()
            request = ChatRequest(
                message="Trigger activated. Please provide vehicle control response.",
                system_context=self._build_system_context(trigger, vehicle_data),
                role="system",
                exclude_history=trigger_ai.exclude_history,
                no_save=trigger_ai.exclude_history,
                model=trigger_ai.model or chat_settings.default_claude_model,
                character_id=trigger_ai.character_id or chat_settings.default_character_id,
                prompt_template_id=(
                    trigger_ai.prompt_template_id or chat_settings.default_prompt_template_id
                ),
            )
            response = await self._chat_service.chat(request)
            if not response.responses:
                self._add_log("  ⚠ LLM returned no response")
                return None

            llm_response = response.responses[0]
            self._add_log(f"  ✓ LLM response received ({len(llm_response)} chars)")
            return llm_response
        except Exception as exc:
            self._add_log(f"  ✗ LLM request failed: {exc}")
            return None

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

    def _execute_command_sequence(self, debug_action: str) -> None:
        items = self._parse_command_sequence(debug_action)
        pending_infinite: list[VehicleCommand] = []

        for item in items:
            if isinstance(item, WaitCommand):
                self._add_log(f"    ⏱ wait {item.milliseconds}ms")
                time.sleep(item.milliseconds / 1000.0)
                continue

            if isinstance(item, WaitUntilCommand):
                self._add_log(f"    ⏳ wait_until {item.condition}")
                self._execute_wait_until(item)
                if pending_infinite:
                    self._add_log(f"    ↻ Resetting {len(pending_infinite)} infinite-duration command(s)")
                    for command in pending_infinite:
                        reset = VehicleCommand(
                            variable=command.variable,
                            value=command.value,
                            duration=1,
                            mode=command.mode,
                        )
                        self._execute_vehicle_command(reset, log_prefix="    ✓ Reset")
                    pending_infinite.clear()
                continue

            self._execute_vehicle_command(item)
            if item.duration == -1:
                pending_infinite.append(item)

            time.sleep(0.05)

    def _execute_vehicle_command(self, command: VehicleCommand, log_prefix: str = "    ✓") -> None:
        actual_duration = 99999 if command.duration == -1 else command.duration
        raw_command = (
            f"DVAWrite {command.variable} {command.value} {actual_duration} {command.mode}"
        )
        self._carmaker_service.execute_command(raw_command)
        duration_label = "99999ms (infinite)" if command.duration == -1 else f"{command.duration}ms"
        self._add_log(
            f"{log_prefix} {command.variable} = {command.value} | {duration_label} | {command.mode}"
        )

    def _execute_wait_until(self, wait_command: WaitUntilCommand) -> None:
        parsed = self._parse_simple_condition(wait_command.condition)
        if parsed is None:
            raise RuntimeError(f"Invalid wait_until condition: {wait_command.condition}")

        start_time = time.time()
        iteration = 0
        while True:
            elapsed_ms = int((time.time() - start_time) * 1000)
            if elapsed_ms > wait_command.timeout:
                raise RuntimeError(f"Timeout after {wait_command.timeout}ms: {wait_command.condition}")

            telemetry = self._carmaker_service.get_telemetry()
            vehicle_data = telemetry.raw_data
            current_value = vehicle_data.get(parsed["variable"])

            if iteration % 10 == 0 and current_value is not None:
                self._add_log(
                    f"    → {parsed['variable']} = {current_value:.4f} (checking {parsed['operator']} {parsed['value']})"
                )

            if current_value is not None and self._evaluate_simple_condition(parsed, current_value):
                self._add_log(f"    ✓ Condition met: {parsed['variable']} = {current_value:.4f}")
                return

            iteration += 1
            time.sleep(0.1)

    def _parse_command_sequence(
        self, text: str
    ) -> list[VehicleCommand | WaitCommand | WaitUntilCommand]:
        items: list[VehicleCommand | WaitCommand | WaitUntilCommand] = []
        code_block_match = re.search(r"```(?:[\w]*)\n([\s\S]*?)\n```", text)
        command_text = code_block_match.group(1) if code_block_match else text

        for raw_line in command_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            wait_match = re.match(r"^wait\s*\(?(\d+)\)?$", line, re.IGNORECASE)
            if wait_match:
                items.append(WaitCommand(milliseconds=int(wait_match.group(1))))
                continue

            wait_until_match = re.match(
                r"^wait_until\s+(.+?)(?:\s+(\d+))?$", line, re.IGNORECASE
            )
            if wait_until_match:
                items.append(
                    WaitUntilCommand(
                        condition=wait_until_match.group(1).strip(),
                        timeout=int(wait_until_match.group(2) or 30000),
                    )
                )
                continue

            command_match = re.match(
                r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*\|\s*(-?\d+)(?:\s*\|\s*(AbsRamp|FacRamp|Abs|Off|Fac))?$",
                line,
                re.IGNORECASE,
            )
            if command_match:
                items.append(
                    VehicleCommand(
                        variable=command_match.group(1),
                        value=float(command_match.group(2)),
                        duration=int(command_match.group(3)),
                        mode=command_match.group(4) or "Abs",
                    )
                )
                continue

            legacy_match = re.match(r"^\s*([A-Za-z0-9._]+)\s*=\s*([0-9.-]+)\s*$", line)
            if legacy_match:
                items.append(
                    VehicleCommand(
                        variable=legacy_match.group(1),
                        value=float(legacy_match.group(2)),
                        duration=2000,
                        mode="Abs",
                    )
                )

        return items

    def _parse_simple_condition(self, condition: str) -> dict[str, str] | None:
        match = re.match(
            r"^\s*([A-Za-z0-9._]+)\s*(>=|<=|==|!=|>|<)\s*([0-9.-]+)\s*$",
            condition,
        )
        if not match:
            return None

        return {
            "variable": match.group(1),
            "operator": match.group(2),
            "value": match.group(3),
        }

    def _evaluate_simple_condition(self, condition: dict[str, str], actual_value: float) -> bool:
        expected = float(condition["value"])
        operator = condition["operator"]

        if operator == ">":
            return actual_value > expected
        if operator == "<":
            return actual_value < expected
        if operator == ">=":
            return actual_value >= expected
        if operator == "<=":
            return actual_value <= expected
        if operator == "==":
            return abs(actual_value - expected) < 1e-4
        if operator == "!=":
            return abs(actual_value - expected) >= 1e-4
        return False

    def _add_log(self, message: str) -> None:
        timestamp = time.strftime("%I:%M:%S %p")
        self._log_messages = [*self._log_messages, f"[{timestamp}] {message}"][-100:]


_settings = get_settings()
_service = TriggerService(
    _settings.data_dir_path / "triggers.json",
    get_carmaker_service(),
    get_chat_service(),
    get_settings_service(),
)


def get_trigger_service() -> TriggerService:
    return _service
