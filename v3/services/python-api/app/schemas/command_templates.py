from datetime import datetime
from pydantic import Field

from app.schemas.common import CamelModel


class CommandTemplate(CamelModel):
    id: int
    name: str
    content: str
    is_active: int
    created_at: datetime
    updated_at: datetime


class CommandTemplateCreate(CamelModel):
    name: str
    content: str
    is_active: int = 1


class CommandTemplateUpdate(CamelModel):
    name: str
    content: str
    is_active: int = 1


class CommandTemplateCollection(CamelModel):
    items: list[CommandTemplate] = Field(default_factory=list)
