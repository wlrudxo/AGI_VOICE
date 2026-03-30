import json
import math
import re
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.services.carmaker import CarMakerService, get_carmaker_service
from app.services.trigger_executor import TriggerExecutor, get_trigger_executor
from app.schemas.triggers import (
    CreateTriggerRequest,
    Trigger,
    TriggerChatEvent,
    TriggerCollection,
    TriggerRuntimeResetResult,
    TriggerRuntimeStatus,
    UpdateTriggerRequest,
    utc_now,
)


@dataclass
class TriggerExecutionJob:
    trigger: Trigger
    vehicle_data: dict[str, float]


class TriggerService:
    def __init__(
        self,
        storage_path: Path,
        carmaker_service: CarMakerService,
        trigger_executor: TriggerExecutor,
    ) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._carmaker_service = carmaker_service
        self._trigger_executor = trigger_executor
        self._triggers: list[Trigger] = []
        self._log_messages: list[str] = []
        self._monitoring_active = False
        self._monitor_thread: threading.Thread | None = None
        self._worker_thread: threading.Thread | None = None
        self._cooldowns: dict[int, float] = {}
        self._is_executing = False
        self._active_trigger_id: int | None = None
        self._pending_jobs: deque[TriggerExecutionJob] = deque()
        self._queued_trigger_ids: set[int] = set()
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
                self._ensure_worker_thread()
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

    def get_runtime_status(self) -> TriggerRuntimeStatus:
        with self._lock:
            return TriggerRuntimeStatus(
                monitoring_active=self._monitoring_active,
                is_executing=self._is_executing,
                active_trigger_id=self._active_trigger_id,
                queued_count=len(self._pending_jobs),
                queued_trigger_ids=list(self._queued_trigger_ids),
            )

    def reset_runtime_state(self) -> TriggerRuntimeResetResult:
        with self._lock:
            was_executing = self._is_executing
            queued_count = len(self._pending_jobs)
            active_trigger_id = self._active_trigger_id
            self._cancel_event.set()
            self._monitoring_active = False
            self._cooldowns.clear()
            self._pending_jobs.clear()
            self._queued_trigger_ids.clear()
            self._active_trigger_id = None
            self._events.clear()
            self._next_event_id = 1
            self._add_log("🛑 Reset Control: trigger monitoring stopped and runtime state cleared")
            return TriggerRuntimeResetResult(
                was_executing=was_executing,
                monitoring_active=self._monitoring_active,
                active_trigger_id=active_trigger_id,
                queued_count=queued_count,
            )

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

    def _ensure_worker_thread(self) -> None:
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return

        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="agi-voice-v3-trigger-worker",
            daemon=True,
        )
        self._worker_thread.start()

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
            if not self._monitoring_active:
                return

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

            if not self._evaluate_expression(trigger.expression, vehicle_data):
                continue

            with self._lock:
                if not self._monitoring_active:
                    return
                next_allowed = self._cooldowns.get(trigger.id, 0.0)
                if now < next_allowed:
                    continue
                if trigger.id == self._active_trigger_id or trigger.id in self._queued_trigger_ids:
                    continue
                self._cooldowns[trigger.id] = now + (trigger.cooldown / 1000.0)
                self._pending_jobs.append(
                    TriggerExecutionJob(
                        trigger=trigger.model_copy(deep=True),
                        vehicle_data=dict(vehicle_data),
                    )
                )
                self._queued_trigger_ids.add(trigger.id)
            self._add_log(f"⚡ Trigger queued: {trigger.name}")

    def _worker_loop(self) -> None:
        while True:
            with self._lock:
                job = self._pending_jobs.popleft() if self._pending_jobs else None
                if job is not None:
                    self._queued_trigger_ids.discard(job.trigger.id)
                    self._is_executing = True
                    self._active_trigger_id = job.trigger.id

            if job is None:
                time.sleep(0.05)
                continue

            self._add_log(f"⚡ Trigger activated: {job.trigger.name}")
            snapshot = ", ".join(
                f"{key}={value:.4f}"
                for key, value in sorted(job.vehicle_data.items())
            )
            self._add_log(f"  Vehicle data: {snapshot}")

            try:
                self._trigger_executor.execute(
                    trigger=job.trigger,
                    vehicle_data=job.vehicle_data,
                    cancel_event=self._cancel_event,
                    is_monitoring_active=self._carmaker_service.is_monitoring_active,
                    set_monitoring_state=self._set_monitoring_state,
                    add_log=self._add_log,
                    add_event=self._add_event,
                )
            except Exception as exc:
                self._add_log(f"✗ Trigger worker error: {exc}")
            finally:
                with self._lock:
                    self._is_executing = False
                    self._active_trigger_id = None
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

    def _add_log(self, message: str) -> None:
        timestamp = time.strftime("%I:%M:%S %p")
        self._log_messages = [*self._log_messages, f"[{timestamp}] {message}"][-100:]

    def _add_event(self, event: TriggerChatEvent) -> None:
        with self._lock:
            next_event = event.model_copy(update={"id": self._next_event_id})
            self._next_event_id += 1
            self._events = [*self._events, next_event][-200:]


_settings = get_settings()
_service = TriggerService(
    _settings.data_dir_path / "triggers.json",
    get_carmaker_service(),
    get_trigger_executor(),
)


def get_trigger_service() -> TriggerService:
    return _service
