from pydantic import Field

from app.schemas.common import CamelModel


class ChatSettings(CamelModel):
    default_character_id: int | None = None
    default_prompt_template_id: int | None = None
    default_claude_model: str = "sonnet"


class TriggerAiSettings(CamelModel):
    exclude_history: bool = True
    character_id: int | None = None
    prompt_template_id: int | None = None
    model: str = "sonnet"


class SettingsData(CamelModel):
    chat: ChatSettings = Field(default_factory=ChatSettings)
    trigger_ai: TriggerAiSettings = Field(default_factory=TriggerAiSettings)
