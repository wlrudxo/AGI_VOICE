import json
import threading
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.ai_catalog import (
    Character,
    CharacterCollection,
    PromptTemplate,
    PromptTemplateCollection,
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

    def _load(self) -> None:
        self._characters = self._load_characters()
        self._prompt_templates = self._load_prompt_templates()

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
