import json
import shutil
import threading
import zipfile
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
            app_settings = self._data.app.model_copy(deep=True)
            if not app_settings.database_file_path:
                app_settings.database_file_path = str(self._resolve_data_dir())
            return app_settings

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
            self._data.app = app_settings.model_copy(deep=True)
            self._data.chat.default_character_id = app_settings.default_character_id
            self._data.chat.default_prompt_template_id = app_settings.default_prompt_template_id
            self._data.chat.default_claude_model = app_settings.default_claude_model
            self._save()
            return self.get_app_settings()

    def get_db_timestamp(self) -> DbTimestamp:
        data_dir = self._resolve_data_dir()
        if not data_dir.exists():
            return DbTimestamp()

        latest_mtime = 0.0
        for path in data_dir.rglob("*"):
            if path.is_file() and "backups" not in path.parts:
                latest_mtime = max(latest_mtime, path.stat().st_mtime)

        if latest_mtime == 0.0:
            return DbTimestamp()

        return DbTimestamp(
            timestamp=datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat(),
            unix_timestamp=latest_mtime,
        )

    def get_db_info(self) -> DbInfo:
        data_dir = self._resolve_data_dir()
        backups_dir = data_dir / "backups"
        data_dir.mkdir(parents=True, exist_ok=True)
        backups_dir.mkdir(parents=True, exist_ok=True)

        total_size = 0
        latest_mtime = 0.0
        for path in data_dir.rglob("*"):
            if path.is_file() and "backups" not in path.parts:
                stat = path.stat()
                total_size += stat.st_size
                latest_mtime = max(latest_mtime, stat.st_mtime)

        backups: list[BackupInfo] = []
        for backup_path in sorted(backups_dir.glob("*.zip"), reverse=True):
            stat = backup_path.stat()
            backups.append(
                BackupInfo(
                    path=str(backup_path),
                    filename=backup_path.name,
                    size_bytes=stat.st_size,
                    size_mb=stat.st_size / 1_048_576.0,
                    created_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                )
            )

        return DbInfo(
            path=str(data_dir),
            size_bytes=total_size,
            size_mb=total_size / 1_048_576.0,
            last_modified=(
                datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()
                if latest_mtime
                else None
            ),
            backups=backups,
        )

    def sync_db_on_shutdown(self) -> str:
        backup_path = self._create_backup("shutdown")
        return f"Database snapshot created: {backup_path}"

    def export_db(self, destination: str) -> str:
        destination_path = Path(destination)
        self._write_snapshot(destination_path)
        return f"Database exported to: {destination_path}"

    def import_db(self, source: str) -> str:
        source_path = Path(source)
        if not source_path.exists():
            raise RuntimeError(f"Import source does not exist: {source}")
        self._extract_snapshot(source_path)
        return f"Database imported from: {source}"

    def sync_db_now(self) -> str:
        database_file_path = self._data.app.database_file_path.strip()
        if not database_file_path:
            raise RuntimeError("No sync folder configured")
        destination_path = Path(database_file_path)
        self._write_snapshot(destination_path)
        return f"Database synced to: {destination_path}"

    def restore_backup(self, backup_path: str) -> str:
        path = Path(backup_path)
        if not path.exists():
            raise RuntimeError(f"Backup does not exist: {backup_path}")
        self._create_backup("pre-restore")
        self._extract_snapshot(path)
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

    def _create_backup(self, prefix: str) -> Path:
        data_dir = self._resolve_data_dir()
        backups_dir = data_dir / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backups_dir / f"{prefix}_{timestamp}.zip"
        self._write_snapshot(backup_path)
        return backup_path

    def _write_snapshot(self, destination_path: Path) -> None:
        data_dir = self._resolve_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(destination_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in data_dir.rglob("*"):
                if not path.is_file():
                    continue
                if path == destination_path:
                    continue
                if "backups" in path.parts:
                    continue
                archive.write(path, arcname=path.relative_to(data_dir))

    def _extract_snapshot(self, source_path: Path) -> None:
        data_dir = self._resolve_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)

        temp_dir = data_dir.parent / f"{data_dir.name}_import_tmp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(source_path, "r") as archive:
                archive.extractall(temp_dir)

            for path in data_dir.iterdir():
                if path.name == "backups":
                    continue
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

            for path in temp_dir.rglob("*"):
                target = data_dir / path.relative_to(temp_dir)
                if path.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


_settings = get_settings()
_service = SettingsService(_settings.data_dir_path / "settings.json")


def get_settings_service() -> SettingsService:
    return _service
