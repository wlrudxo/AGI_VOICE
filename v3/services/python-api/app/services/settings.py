import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.settings import (
    AutonomousDrivingSettings,
    AppSettings,
    BackupInfo,
    ChatSettings,
    DbInfo,
    DbTimestamp,
    PromptContextSettings,
    SettingsData,
    TriggerAiSettings,
)
from app.services.ai_chat_db import get_ai_chat_db


class SettingsService:
    def __init__(self, storage_path: Path) -> None:
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._data = SettingsData()
        self._load()

    def get_chat_settings(self) -> ChatSettings:
        with self._lock:
            chat = self._data.chat.model_copy(deep=True)
            if chat.default_character_id is None:
                chat.default_character_id = self._data.app.default_character_id
            if chat.default_prompt_template_id is None:
                chat.default_prompt_template_id = self._data.app.default_prompt_template_id
            if not chat.default_claude_model:
                chat.default_claude_model = self._data.app.default_claude_model
            return chat

    def update_chat_settings(self, chat_settings: ChatSettings) -> ChatSettings:
        with self._lock:
            self._data.chat = chat_settings.model_copy(deep=True)
            self._data.app.default_character_id = chat_settings.default_character_id
            self._data.app.default_prompt_template_id = chat_settings.default_prompt_template_id
            self._data.app.default_claude_model = chat_settings.default_claude_model
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

    def get_autonomous_driving_settings(self) -> AutonomousDrivingSettings:
        with self._lock:
            return self._data.autonomous_driving.model_copy(deep=True)

    def update_autonomous_driving_settings(
        self,
        autonomous_driving: AutonomousDrivingSettings,
    ) -> AutonomousDrivingSettings:
        with self._lock:
            self._data.autonomous_driving = autonomous_driving.model_copy(deep=True)
            self._save()
            return self._data.autonomous_driving.model_copy(deep=True)

    def get_app_settings(self) -> AppSettings:
        with self._lock:
            return self._data.app.model_copy(deep=True)

    def get_prompt_context_settings(self) -> PromptContextSettings:
        with self._lock:
            return self._data.prompt_context.model_copy(deep=True)

    def update_prompt_context_settings(
        self,
        prompt_context: PromptContextSettings,
    ) -> PromptContextSettings:
        with self._lock:
            self._data.prompt_context = prompt_context.model_copy(deep=True)
            self._save()
            return self._data.prompt_context.model_copy(deep=True)

    def update_app_settings(self, app_settings: AppSettings) -> AppSettings:
        with self._lock:
            self._validate_app_settings(app_settings)
            self._data.app = app_settings.model_copy(deep=True)
            self._data.chat.default_character_id = app_settings.default_character_id
            self._data.chat.default_prompt_template_id = app_settings.default_prompt_template_id
            self._data.chat.default_claude_model = app_settings.default_claude_model
            self._save()
            return self.get_app_settings()

    def get_db_timestamp(self) -> DbTimestamp:
        db_path = self._resolve_ai_chat_db_path()
        if not db_path.exists():
            return DbTimestamp()
        latest_mtime = db_path.stat().st_mtime

        return DbTimestamp(
            timestamp=datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat(),
            unix_timestamp=latest_mtime,
        )

    def get_db_info(self) -> DbInfo:
        db_path = self._resolve_ai_chat_db_path()
        if not db_path.exists():
            raise RuntimeError("Database file does not exist")

        backups_dir = self._resolve_backup_dir()
        backups_dir.mkdir(parents=True, exist_ok=True)
        stat = db_path.stat()

        backups: list[BackupInfo] = []
        for backup_path in self._list_backup_paths():
            backup_stat = backup_path.stat()
            backups.append(
                BackupInfo(
                    path=str(backup_path),
                    filename=backup_path.name,
                    size_bytes=backup_stat.st_size,
                    size_mb=backup_stat.st_size / 1_048_576.0,
                    created_at=datetime.fromtimestamp(
                        backup_stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                )
            )

        return DbInfo(
            path=str(db_path),
            size_bytes=stat.st_size,
            size_mb=stat.st_size / 1_048_576.0,
            last_modified=(
                datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            ),
            backups=backups,
        )

    def sync_db_on_shutdown(self) -> str:
        lines: list[str] = []

        try:
            backup_path = self._create_backup()
            lines.append(f"Backup created: {backup_path}")
        except RuntimeError as exc:
            lines.append(f"Backup failed: {exc}")

        try:
            self._cleanup_old_backups(5)
            lines.append("Old backups cleaned up")
        except RuntimeError as exc:
            lines.append(f"Cleanup failed: {exc}")

        sync_path = self._resolve_sync_db_path()
        if sync_path is None:
            lines.append("No sync folder configured")
        else:
            try:
                self._copy_db_to(sync_path)
                lines.append(f"Synced to: {sync_path}")
            except RuntimeError as exc:
                lines.append(f"Sync failed: {exc}")

        return "\n".join(lines)

    def export_db(self, destination: str) -> str:
        destination_path = Path(destination)
        self._copy_db_to(destination_path, create_parent=True)
        return f"Database exported to: {destination_path}"

    def import_db(self, source: str) -> str:
        source_path = Path(source)
        if not source_path.exists():
            raise RuntimeError(f"Import source does not exist: {source}")
        if not source_path.is_file():
            raise RuntimeError(f"Import source is not a file: {source}")

        db_path = self._resolve_ai_chat_db_path()
        if db_path.exists():
            self._create_backup()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, db_path)
        return f"Database imported from: {source}"

    def sync_db_now(self) -> str:
        destination_path = self._resolve_sync_db_path()
        if destination_path is None:
            raise RuntimeError("No sync folder configured")
        parent = destination_path.parent
        if parent and not parent.exists():
            raise RuntimeError(f"Sync folder parent directory does not exist: {parent!r}")
        self._copy_db_to(destination_path)
        return f"Database synced to: {destination_path}"

    def restore_backup(self, backup_path: str) -> str:
        path = Path(backup_path)
        if not path.exists():
            raise RuntimeError(f"Backup does not exist: {backup_path}")
        if not path.is_file():
            raise RuntimeError(f"Backup path is not a file: {backup_path}")
        self.import_db(backup_path)
        return f"Database restored from: {backup_path}"

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

    def _resolve_data_dir(self) -> Path:
        return get_settings().data_dir_path

    def _resolve_ai_chat_db_path(self) -> Path:
        # App-settings DB management in V2 targets ai_chat.db specifically, not an archive of the
        # entire data directory. Keep the same contract in the Python port.
        return get_ai_chat_db().db_path

    def _resolve_backup_dir(self) -> Path:
        return self._resolve_data_dir() / "backups"

    def _resolve_sync_db_path(self) -> Path | None:
        raw_path = self._data.app.database_file_path.strip()
        if not raw_path:
            return None
        return Path(raw_path)

    def _validate_app_settings(self, app_settings: AppSettings) -> None:
        if app_settings.claude_workspace_dir.strip():
            workspace_path = Path(app_settings.claude_workspace_dir.strip())
            if not workspace_path.exists():
                raise RuntimeError(f"Directory does not exist: {app_settings.claude_workspace_dir}")
            if not workspace_path.is_dir():
                raise RuntimeError(f"Path is not a directory: {app_settings.claude_workspace_dir}")

        if app_settings.database_file_path.strip():
            db_path = Path(app_settings.database_file_path.strip())
            parent = db_path.parent
            if not str(parent):
                raise RuntimeError("Invalid database path")
            if not parent.exists():
                raise RuntimeError(f"Parent directory does not exist: {parent!r}")
            if db_path.exists() and not db_path.is_file():
                raise RuntimeError(f"Path exists but is not a file: {app_settings.database_file_path}")

    def _create_backup(self) -> Path:
        db_path = self._resolve_ai_chat_db_path()
        if not db_path.exists():
            raise RuntimeError("Database file does not exist")

        backups_dir = self._resolve_backup_dir()
        backups_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backups_dir / f"agi_voice_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        return backup_path

    def _list_backup_paths(self) -> list[Path]:
        backups_dir = self._resolve_backup_dir()
        if not backups_dir.exists():
            return []

        backups = [
            path
            for path in backups_dir.iterdir()
            if path.is_file() and path.name.startswith("agi_voice_backup_") and path.suffix == ".db"
        ]
        backups.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        return backups

    def _cleanup_old_backups(self, keep_count: int) -> None:
        for backup_path in self._list_backup_paths()[keep_count:]:
            backup_path.unlink()

    def _copy_db_to(self, destination_path: Path, *, create_parent: bool = False) -> None:
        db_path = self._resolve_ai_chat_db_path()
        if not db_path.exists():
            raise RuntimeError("Database file does not exist")
        if create_parent:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_path, destination_path)


_settings = get_settings()
_service = SettingsService(_settings.data_dir_path / "settings.json")


def get_settings_service() -> SettingsService:
    return _service
