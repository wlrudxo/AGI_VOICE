from datetime import datetime, timezone
from pydantic import Field

from app.schemas.common import CamelModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Character(CamelModel):
    id: int
    name: str
    prompt_content: str
    created_at: datetime
    updated_at: datetime


class PromptTemplate(CamelModel):
    id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime


class CharacterCollection(CamelModel):
    items: list[Character] = Field(default_factory=list)


class PromptTemplateCollection(CamelModel):
    items: list[PromptTemplate] = Field(default_factory=list)
