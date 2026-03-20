from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MapsHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "maps"


@router.get("/health", response_model=MapsHealthResponse)
async def maps_health() -> MapsHealthResponse:
    return MapsHealthResponse()

