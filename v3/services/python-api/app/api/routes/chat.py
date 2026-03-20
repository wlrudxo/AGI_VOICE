from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService, get_chat_service

router = APIRouter()


class ChatHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "chat"


@router.get("/health", response_model=ChatHealthResponse)
async def chat_health() -> ChatHealthResponse:
    return ChatHealthResponse()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        return await service.chat(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
