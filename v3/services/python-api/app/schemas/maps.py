from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import CamelModel


class MapRecord(CamelModel):
    id: int
    name: str
    description: str
    node_xml: str
    edge_xml: str
    tags: str | None = None
    category: str
    difficulty: str
    metadata: str | None = None
    is_embedded: int
    embedded_at: datetime | None = None
    embedding_model: str | None = None
    created_at: datetime
    updated_at: datetime


class CreateMapRequest(CamelModel):
    name: str
    description: str
    node_xml: str
    edge_xml: str
    tags: list[str] | None = None
    category: str | None = None
    difficulty: str | None = None
    metadata: dict[str, Any] | None = None


class UpdateMapRequest(CamelModel):
    name: str | None = None
    description: str | None = None
    node_xml: str | None = None
    edge_xml: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    difficulty: str | None = None
    metadata: dict[str, Any] | None = None


class GetMapsQuery(CamelModel):
    category: str | None = None
    is_embedded: bool | None = None
    search: str | None = None


class EmbedResult(CamelModel):
    success: bool
    map_id: int | None = None
    map_name: str | None = None
    embedded_at: str | None = None
    embedding_model: str | None = None
    error: str | None = None


class MapSearchResult(CamelModel):
    map_id: int
    map_name: str
    description: str
    category: str
    difficulty: str
    tags: list[str] = Field(default_factory=list)
    similarity_score: float
    distance: float
    is_embedded: bool


class BuildResult(CamelModel):
    success: bool
    total_maps: int | None = None
    embedded_count: int | None = None
    skipped_count: int | None = None
    embedding_model: str | None = None
    index_path: str | None = None
    error: str | None = None
