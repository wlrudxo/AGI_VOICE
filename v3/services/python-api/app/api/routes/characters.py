from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.ai_catalog import Character, CharacterCreate, CharacterUpdate
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service
from app.schemas.conversations import DeleteResult

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


@router.post("", response_model=Character)
def create_character(
    character_data: CharacterCreate,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> Character:
    return service.create_character(character_data)


@router.put("/{character_id}", response_model=Character)
def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> Character:
    try:
        return service.update_character(character_id, character_data)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{character_id}", response_model=DeleteResult)
def delete_character(
    character_id: int,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> DeleteResult:
    try:
        service.delete_character(character_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteResult(message="Character deleted successfully")
