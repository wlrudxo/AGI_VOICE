import json
import threading
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.settings import ChatSettings, SettingsData, TriggerAiSettings


class SettingsService:
    def __init__(self, storage_path: Path) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._data = SettingsData()
        self._load()

    def get_chat_settings(self) -> ChatSettings:
        with self._lock:
            return self._data.chat.model_copy(deep=True)

    def update_chat_settings(self, chat_settings: ChatSettings) -> ChatSettings:
        with self._lock:
            self._data.chat = chat_settings.model_copy(deep=True)
            self._save()
            return self._data.chat.model_copy(deep=True)

    def get_trigger_ai_settings(self) -> TriggerAiSettings:
        with self._lock:
            return self._data.trigger_ai.model_copy(deep=True)

    def update_trigger_ai_settings(self, trigger_ai: TriggerAiSettings) -> TriggerAiSettings:
        with self._lock:
            self._data.trigger_ai = trigger_ai.model_copy(deep=True)
            self._save()
            return self._data.trigger_ai.model_copy(deep=True)

    def _load(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._save()
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            self._data = SettingsData.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError):
            self._data = SettingsData()
            self._save()

    def _save(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            self._data.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )


_settings = get_settings()
_service = SettingsService(_settings.data_dir_path / "settings.json")


def get_settings_service() -> SettingsService:
    return _service
