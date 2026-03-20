from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SettingsHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "settings"


@router.get("/health", response_model=SettingsHealthResponse)
async def settings_health() -> SettingsHealthResponse:
    return SettingsHealthResponse()

