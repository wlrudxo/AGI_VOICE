from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.settings import (
    AppSettings,
    AutonomousDrivingSettings,
    ChatSettings,
    DbInfo,
    DbTimestamp,
    PromptContextSettings,
    TriggerAiSettings,
)
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


@router.get("/autonomous-driving", response_model=AutonomousDrivingSettings)
def get_autonomous_driving_settings(
    service: SettingsService = Depends(get_settings_service),
) -> AutonomousDrivingSettings:
    return service.get_autonomous_driving_settings()


@router.put("/autonomous-driving", response_model=AutonomousDrivingSettings)
def update_autonomous_driving_settings(
    autonomous_driving: AutonomousDrivingSettings,
    service: SettingsService = Depends(get_settings_service),
) -> AutonomousDrivingSettings:
    return service.update_autonomous_driving_settings(autonomous_driving)


@router.get("/prompt-context", response_model=PromptContextSettings)
def get_prompt_context_settings(
    service: SettingsService = Depends(get_settings_service),
) -> PromptContextSettings:
    return service.get_prompt_context_settings()


@router.put("/prompt-context", response_model=PromptContextSettings)
def update_prompt_context_settings(
    prompt_context: PromptContextSettings,
    service: SettingsService = Depends(get_settings_service),
) -> PromptContextSettings:
    return service.update_prompt_context_settings(prompt_context)


@router.get("/app", response_model=AppSettings)
def get_app_settings(
    service: SettingsService = Depends(get_settings_service),
) -> AppSettings:
    return service.get_app_settings()


@router.put("/app", response_model=AppSettings)
def update_app_settings(
    app_settings: AppSettings,
    service: SettingsService = Depends(get_settings_service),
) -> AppSettings:
    return service.update_app_settings(app_settings)


@router.get("/db/timestamp", response_model=DbTimestamp)
def get_db_timestamp(
    service: SettingsService = Depends(get_settings_service),
) -> DbTimestamp:
    return service.get_db_timestamp()


@router.get("/db/info", response_model=DbInfo)
def get_db_info(
    service: SettingsService = Depends(get_settings_service),
) -> DbInfo:
    return service.get_db_info()


class ExportDbRequest(BaseModel):
    destination: str


class ImportDbRequest(BaseModel):
    source: str


class RestoreBackupRequest(BaseModel):
    backup_path: str


class ActionResponse(BaseModel):
    message: str


@router.post("/db/export", response_model=ActionResponse)
def export_db(
    request: ExportDbRequest,
    service: SettingsService = Depends(get_settings_service),
) -> ActionResponse:
    return ActionResponse(message=service.export_db(request.destination))


@router.post("/db/import", response_model=ActionResponse)
def import_db(
    request: ImportDbRequest,
    service: SettingsService = Depends(get_settings_service),
) -> ActionResponse:
    return ActionResponse(message=service.import_db(request.source))


@router.post("/db/sync", response_model=ActionResponse)
def sync_db_now(
    service: SettingsService = Depends(get_settings_service),
) -> ActionResponse:
    return ActionResponse(message=service.sync_db_now())


@router.post("/db/sync-shutdown", response_model=ActionResponse)
def sync_db_on_shutdown(
    service: SettingsService = Depends(get_settings_service),
) -> ActionResponse:
    return ActionResponse(message=service.sync_db_on_shutdown())


@router.post("/db/restore", response_model=ActionResponse)
def restore_backup(
    request: RestoreBackupRequest,
    service: SettingsService = Depends(get_settings_service),
) -> ActionResponse:
    return ActionResponse(message=service.restore_backup(request.backup_path))
