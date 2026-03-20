from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.ai_catalog import PromptTemplate
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service

router = APIRouter()


class PromptTemplatesHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "prompt_templates"


@router.get("/health", response_model=PromptTemplatesHealthResponse)
async def prompt_templates_health() -> PromptTemplatesHealthResponse:
    return PromptTemplatesHealthResponse()


@router.get("", response_model=list[PromptTemplate])
def get_prompt_templates(
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> list[PromptTemplate]:
    return service.list_prompt_templates()
