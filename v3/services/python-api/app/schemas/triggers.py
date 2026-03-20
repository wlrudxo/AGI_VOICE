from datetime import datetime, timezone

from pydantic import Field

from app.schemas.common import CamelModel


def default_cooldown() -> int:
    return 5000


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Trigger(CamelModel):
    id: int
    name: str
    is_active: bool = True
    expression: str
    message: str
    conversation_id: int | None = None
    use_rule_control: bool = False
    debug_action: str = ""
    cooldown: int = default_cooldown()
    created_at: datetime
    updated_at: datetime


class CreateTriggerRequest(CamelModel):
    name: str
    expression: str
    message: str
    conversation_id: int | None = None
    use_rule_control: bool = False
    debug_action: str = ""
    cooldown: int = default_cooldown()


class UpdateTriggerRequest(CamelModel):
    name: str
    expression: str
    message: str
    conversation_id: int | None = None
    use_rule_control: bool = False
    debug_action: str = ""
    cooldown: int = default_cooldown()


class TriggerCollection(CamelModel):
    version: str = "1.0"
    triggers: list[Trigger] = Field(default_factory=list)
