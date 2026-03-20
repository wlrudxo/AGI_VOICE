from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.settings import ChatSettings, TriggerAiSettings
from app.services.settings import SettingsService, get_settings_service

router = APIRouter()


class SettingsHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "settings"


@router.get("/health", response_model=SettingsHealthResponse)
async def settings_health() -> SettingsHealthResponse:
    return SettingsHealthResponse()


@router.get("/chat", response_model=ChatSettings)
def get_chat_settings(
    service: SettingsService = Depends(get_settings_service),
) -> ChatSettings:
    return service.get_chat_settings()


@router.put("/chat", response_model=ChatSettings)
def update_chat_settings(
    chat_settings: ChatSettings,
    service: SettingsService = Depends(get_settings_service),
) -> ChatSettings:
    return service.update_chat_settings(chat_settings)


@router.get("/trigger-ai", response_model=TriggerAiSettings)
def get_trigger_ai_settings(
    service: SettingsService = Depends(get_settings_service),
) -> TriggerAiSettings:
    return service.get_trigger_ai_settings()


@router.put("/trigger-ai", response_model=TriggerAiSettings)
def update_trigger_ai_settings(
    trigger_ai: TriggerAiSettings,
    service: SettingsService = Depends(get_settings_service),
) -> TriggerAiSettings:
    return service.update_trigger_ai_settings(trigger_ai)
