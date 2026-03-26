from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.ai_catalog import (
    PromptTemplate,
    PromptTemplateCreate,
    PromptTemplateUpdate,
)
from app.services.ai_catalog import AiCatalogService, get_ai_catalog_service
from app.schemas.conversations import DeleteResult

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


@router.post("", response_model=PromptTemplate)
def create_prompt_template(
    template_data: PromptTemplateCreate,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> PromptTemplate:
    return service.create_prompt_template(template_data)


@router.put("/{template_id}", response_model=PromptTemplate)
def update_prompt_template(
    template_id: int,
    template_data: PromptTemplateUpdate,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> PromptTemplate:
    try:
        return service.update_prompt_template(template_id, template_data)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{template_id}", response_model=DeleteResult)
def delete_prompt_template(
    template_id: int,
    service: AiCatalogService = Depends(get_ai_catalog_service),
) -> DeleteResult:
    try:
        service.delete_prompt_template(template_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteResult(message="Prompt template deleted successfully")
