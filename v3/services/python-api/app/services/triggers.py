import json
import math
import re
import threading
import time
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.services.carmaker import CarMakerService, get_carmaker_service
from app.schemas.triggers import (
    CreateTriggerRequest,
    Trigger,
    TriggerCollection,
    UpdateTriggerRequest,
    utc_now,
)


class TriggerService:
    def __init__(self, storage_path: Path, carmaker_service: CarMakerService) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._carmaker_service = carmaker_service
        self._triggers: list[Trigger] = []
        self._log_messages: list[str] = []
        self._monitoring_active = False
        self._monitor_thread: threading.Thread | None = None
        self._cooldowns: dict[int, float] = {}
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
            self._add_log("  → Trigger action pipeline pending backend migration")

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

    def _add_log(self, message: str) -> None:
        timestamp = time.strftime("%I:%M:%S %p")
        self._log_messages = [*self._log_messages, f"[{timestamp}] {message}"][-100:]


_settings = get_settings()
_service = TriggerService(_settings.data_dir_path / "triggers.json", get_carmaker_service())


def get_trigger_service() -> TriggerService:
    return _service
