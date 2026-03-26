import json
import threading
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.ai_catalog import utc_now
from app.schemas.command_templates import (
    CommandTemplate,
    CommandTemplateCollection,
    CommandTemplateCreate,
    CommandTemplateUpdate,
)


class CommandTemplateService:
    def __init__(self, storage_path: Path) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._templates: list[CommandTemplate] = []
        self._load()

    def list_templates(self, is_active: int | None = None) -> list[CommandTemplate]:
        with self._lock:
            items = self._templates
            if is_active is not None:
                items = [item for item in items if item.is_active == is_active]
            return [item.model_copy(deep=True) for item in items]

    def create_template(self, payload: CommandTemplateCreate) -> CommandTemplate:
        with self._lock:
            template = CommandTemplate(
                id=self._next_id(),
                name=payload.name,
                content=payload.content,
                is_active=payload.is_active,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            self._templates.append(template)
            self._save()
            return template.model_copy(deep=True)

    def update_template(self, template_id: int, payload: CommandTemplateUpdate) -> CommandTemplate:
        with self._lock:
            index, existing = self._require_template(template_id)
            updated = CommandTemplate(
                id=existing.id,
                name=payload.name,
                content=payload.content,
                is_active=payload.is_active,
                created_at=existing.created_at,
                updated_at=utc_now(),
            )
            self._templates[index] = updated
            self._save()
            return updated.model_copy(deep=True)

    def toggle_template(self, template_id: int) -> CommandTemplate:
        with self._lock:
            index, existing = self._require_template(template_id)
            updated = existing.model_copy(
                update={
                    "is_active": 0 if existing.is_active == 1 else 1,
                    "updated_at": utc_now(),
                }
            )
            self._templates[index] = updated
            self._save()
            return updated.model_copy(deep=True)

    def delete_template(self, template_id: int) -> None:
        with self._lock:
            index, _ = self._require_template(template_id)
            self._templates.pop(index)
            self._save()

    def _load(self) -> None:
        default_items = [
            CommandTemplate(
                id=1,
                name="Map Management Commands",
                content="Use map management tags when the user asks to create, read, update, or delete maps.",
                is_active=1,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        ]
        default_value = CommandTemplateCollection(items=default_items)

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._storage_path.write_text(
                default_value.model_dump_json(indent=2, by_alias=True),
                encoding="utf-8",
            )
            self._templates = list(default_items)
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            collection = CommandTemplateCollection.model_validate(payload)
            self._templates = list(collection.items)
        except (OSError, json.JSONDecodeError, ValidationError):
            self._storage_path.write_text(
                default_value.model_dump_json(indent=2, by_alias=True),
                encoding="utf-8",
            )
            self._templates = list(default_items)

    def _save(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            CommandTemplateCollection(items=self._templates).model_dump_json(
                indent=2, by_alias=True
            ),
            encoding="utf-8",
        )

    def _next_id(self) -> int:
        return max((item.id for item in self._templates), default=0) + 1

    def _require_template(self, template_id: int) -> tuple[int, CommandTemplate]:
        for index, item in enumerate(self._templates):
            if item.id == template_id:
                return index, item
        raise RuntimeError("Command template not found")


_settings = get_settings()
_service = CommandTemplateService(_settings.data_dir_path / "command_templates.json")


def get_command_template_service() -> CommandTemplateService:
    return _service
