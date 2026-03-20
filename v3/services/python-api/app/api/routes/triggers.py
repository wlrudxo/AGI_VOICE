from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TriggerHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "triggers"


@router.get("/health", response_model=TriggerHealthResponse)
async def triggers_health() -> TriggerHealthResponse:
    return TriggerHealthResponse()

