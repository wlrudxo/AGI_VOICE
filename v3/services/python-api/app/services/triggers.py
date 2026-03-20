import json
import threading
from pathlib import Path

from app.core.config import get_settings
from app.schemas.triggers import (
    CreateTriggerRequest,
    Trigger,
    TriggerCollection,
    UpdateTriggerRequest,
    utc_now,
)


class TriggerService:
    def __init__(self, storage_path: Path) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._triggers: list[Trigger] = []
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

        collection = TriggerCollection.model_validate(payload)
        self._triggers = list(collection.triggers)

    def _save(self) -> None:
        payload = TriggerCollection(triggers=self._triggers)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            payload.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )


_settings = get_settings()
_service = TriggerService(_settings.data_dir_path / "triggers.json")


def get_trigger_service() -> TriggerService:
    return _service
