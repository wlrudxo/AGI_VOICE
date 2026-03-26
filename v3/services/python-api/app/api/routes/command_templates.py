from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.schemas.command_templates import (
    CommandTemplate,
    CommandTemplateCreate,
    CommandTemplateUpdate,
)
from app.schemas.conversations import DeleteResult
from app.services.command_templates import (
    CommandTemplateService,
    get_command_template_service,
)

router = APIRouter()


class CommandTemplatesHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "command_templates"


@router.get("/health", response_model=CommandTemplatesHealthResponse)
async def command_templates_health() -> CommandTemplatesHealthResponse:
    return CommandTemplatesHealthResponse()


@router.get("", response_model=list[CommandTemplate])
def get_command_templates(
    is_active: int | None = Query(default=None),
    service: CommandTemplateService = Depends(get_command_template_service),
) -> list[CommandTemplate]:
    return service.list_templates(is_active)


@router.post("", response_model=CommandTemplate)
def create_command_template(
    template_data: CommandTemplateCreate,
    service: CommandTemplateService = Depends(get_command_template_service),
) -> CommandTemplate:
    return service.create_template(template_data)


@router.put("/{template_id}", response_model=CommandTemplate)
def update_command_template(
    template_id: int,
    template_data: CommandTemplateUpdate,
    service: CommandTemplateService = Depends(get_command_template_service),
) -> CommandTemplate:
    try:
        return service.update_template(template_id, template_data)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/toggle", response_model=CommandTemplate)
def toggle_command_template(
    template_id: int,
    service: CommandTemplateService = Depends(get_command_template_service),
) -> CommandTemplate:
    try:
        return service.toggle_template(template_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{template_id}", response_model=DeleteResult)
def delete_command_template(
    template_id: int,
    service: CommandTemplateService = Depends(get_command_template_service),
) -> DeleteResult:
    try:
        service.delete_template(template_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteResult(message="Command template deleted successfully")
