from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CarMakerHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "carmaker"


@router.get("/health", response_model=CarMakerHealthResponse)
async def carmaker_health() -> CarMakerHealthResponse:
    return CarMakerHealthResponse()

