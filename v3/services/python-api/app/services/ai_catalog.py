import json
import threading
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.ai_catalog import (
    Character,
    CharacterCreate,
    CharacterCollection,
    CharacterUpdate,
    PromptTemplate,
    PromptTemplateCreate,
    PromptTemplateCollection,
    PromptTemplateUpdate,
    utc_now,
)


class AiCatalogService:
    def __init__(self, characters_path: Path, prompt_templates_path: Path) -> None:
        self._lock = threading.RLock()
        self._characters_path = characters_path
        self._prompt_templates_path = prompt_templates_path
        self._characters: list[Character] = []
        self._prompt_templates: list[PromptTemplate] = []
        self._load()

    def list_characters(self) -> list[Character]:
        with self._lock:
            return [item.model_copy(deep=True) for item in self._characters]

    def list_prompt_templates(self) -> list[PromptTemplate]:
        with self._lock:
            return [item.model_copy(deep=True) for item in self._prompt_templates]

    def create_character(self, payload: CharacterCreate) -> Character:
        with self._lock:
            character = Character(
                id=self._next_id(self._characters),
                name=payload.name,
                prompt_content=payload.prompt_content,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            self._characters.append(character)
            self._save_characters()
            return character.model_copy(deep=True)

    def update_character(self, character_id: int, payload: CharacterUpdate) -> Character:
        with self._lock:
            index, existing = self._require_item(self._characters, character_id, "Character")
            updated = Character(
                id=existing.id,
                name=payload.name,
                prompt_content=payload.prompt_content,
                created_at=existing.created_at,
                updated_at=utc_now(),
            )
            self._characters[index] = updated
            self._save_characters()
            return updated.model_copy(deep=True)

    def delete_character(self, character_id: int) -> None:
        with self._lock:
            index, _ = self._require_item(self._characters, character_id, "Character")
            self._characters.pop(index)
            self._save_characters()

    def create_prompt_template(self, payload: PromptTemplateCreate) -> PromptTemplate:
        with self._lock:
            template = PromptTemplate(
                id=self._next_id(self._prompt_templates),
                name=payload.name,
                content=payload.content,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            self._prompt_templates.append(template)
            self._save_prompt_templates()
            return template.model_copy(deep=True)

    def update_prompt_template(
        self,
        template_id: int,
        payload: PromptTemplateUpdate,
    ) -> PromptTemplate:
        with self._lock:
            index, existing = self._require_item(
                self._prompt_templates, template_id, "Prompt template"
            )
            updated = PromptTemplate(
                id=existing.id,
                name=payload.name,
                content=payload.content,
                created_at=existing.created_at,
                updated_at=utc_now(),
            )
            self._prompt_templates[index] = updated
            self._save_prompt_templates()
            return updated.model_copy(deep=True)

    def delete_prompt_template(self, template_id: int) -> None:
        with self._lock:
            index, _ = self._require_item(self._prompt_templates, template_id, "Prompt template")
            self._prompt_templates.pop(index)
            self._save_prompt_templates()

    def _load(self) -> None:
        self._characters = self._load_characters()
        self._prompt_templates = self._load_prompt_templates()

    def _save_characters(self) -> None:
        self._characters_path.parent.mkdir(parents=True, exist_ok=True)
        self._characters_path.write_text(
            CharacterCollection(items=self._characters).model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )

    def _save_prompt_templates(self) -> None:
        self._prompt_templates_path.parent.mkdir(parents=True, exist_ok=True)
        self._prompt_templates_path.write_text(
            PromptTemplateCollection(items=self._prompt_templates).model_dump_json(
                indent=2, by_alias=True
            ),
            encoding="utf-8",
        )

    def _next_id(self, items: list[Character] | list[PromptTemplate]) -> int:
        return max((item.id for item in items), default=0) + 1

    def _require_item(self, items, item_id: int, label: str):
        for index, item in enumerate(items):
            if item.id == item_id:
                return index, item
        raise RuntimeError(f"{label} not found")

    def _load_characters(self) -> list[Character]:
        default_items = [
            Character(
                id=1,
                name="Professional Research Assistant",
                prompt_content="You are a professional research assistant focused on safe, precise vehicle guidance.",
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        ]
        return self._load_collection(
            self._characters_path,
            CharacterCollection,
            CharacterCollection(items=default_items),
        ).items

    def _load_prompt_templates(self) -> list[PromptTemplate]:
        default_items = [
            PromptTemplate(
                id=1,
                name="Default Vehicle Control",
                content="Provide concise vehicle control commands based on the trigger context and current vehicle data.",
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        ]
        return self._load_collection(
            self._prompt_templates_path,
            PromptTemplateCollection,
            PromptTemplateCollection(items=default_items),
        ).items

    def _load_collection(self, path: Path, schema_cls, default_value):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(default_value.model_dump_json(indent=2, by_alias=True), encoding="utf-8")
            return default_value

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return schema_cls.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError):
            path.write_text(default_value.model_dump_json(indent=2, by_alias=True), encoding="utf-8")
            return default_value


_settings = get_settings()
_service = AiCatalogService(
    _settings.data_dir_path / "characters.json",
    _settings.data_dir_path / "prompt_templates.json",
)


def get_ai_catalog_service() -> AiCatalogService:
    return _service
