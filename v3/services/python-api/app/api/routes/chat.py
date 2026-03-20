from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "chat"


@router.get("/health", response_model=ChatHealthResponse)
async def chat_health() -> ChatHealthResponse:
    return ChatHealthResponse()

