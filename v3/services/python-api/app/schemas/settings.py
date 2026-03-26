from pydantic import Field

from app.schemas.common import CamelModel


class AppSettings(CamelModel):
    claude_workspace_dir: str = ""
    database_file_path: str = ""
    database_backup_enabled: bool = True
    default_character_id: int | None = None
    default_prompt_template_id: int | None = None
    keep_conversation_prompts: bool = True
    default_claude_model: str = "sonnet"


class ChatSettings(CamelModel):
    default_character_id: int | None = None
    default_prompt_template_id: int | None = None
    default_claude_model: str = "sonnet"


class TriggerAiSettings(CamelModel):
    exclude_history: bool = True
    character_id: int | None = None
    prompt_template_id: int | None = None
    model: str = "sonnet"


class DbTimestamp(CamelModel):
    timestamp: str | None = None
    unix_timestamp: float | None = None


class BackupInfo(CamelModel):
    path: str
    filename: str
    size_bytes: int
    size_mb: float
    created_at: str | None = None


class DbInfo(CamelModel):
    path: str
    size_bytes: int
    size_mb: float
    last_modified: str | None = None
    backups: list[BackupInfo] = Field(default_factory=list)


class SettingsData(CamelModel):
    app: AppSettings = Field(default_factory=AppSettings)
    chat: ChatSettings = Field(default_factory=ChatSettings)
    trigger_ai: TriggerAiSettings = Field(default_factory=TriggerAiSettings)
