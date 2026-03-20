from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.ai_catalog import Character
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service

router = APIRouter()


class CharactersHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "characters"


@router.get("/health", response_model=CharactersHealthResponse)
async def characters_health() -> CharactersHealthResponse:
    return CharactersHealthResponse()


@router.get("", response_model=list[Character])
def get_characters(
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> list[Character]:
    return service.list_characters()
