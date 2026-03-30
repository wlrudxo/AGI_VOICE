from pydantic import Field

from app.schemas.common import CamelModel


class PromptTemplate(CamelModel):
    id: int
    name: str
    content: str
    created_at: str
    updated_at: str


class PromptTemplateCreate(CamelModel):
    name: str
    content: str


class PromptTemplateUpdate(CamelModel):
    name: str
    content: str


class PromptTemplateCollection(CamelModel):
    items: list[PromptTemplate] = Field(default_factory=list)
