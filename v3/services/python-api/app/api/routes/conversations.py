from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.schemas.conversations import (
    ConversationResponse,
    ConversationUpdate,
    ConversationWithCount,
    DeleteResult,
    MessageResponse,
)
from app.services.chat import ChatService, get_chat_service

router = APIRouter()


class ConversationsHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "conversations"


@router.get("/health", response_model=ConversationsHealthResponse)
async def conversations_health() -> ConversationsHealthResponse:
    return ConversationsHealthResponse()


@router.get("", response_model=list[ConversationWithCount])
def get_conversations(
    service: ChatService = Depends(get_chat_service),
) -> list[ConversationWithCount]:
    return service.get_conversations()


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation_by_id(
    conversation_id: int,
    service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    try:
        return service.get_conversation_by_id(conversation_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    service: ChatService = Depends(get_chat_service),
) -> list[MessageResponse]:
    try:
        return service.get_conversation_messages(conversation_id, limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    service: ChatService = Depends(get_chat_service),
) -> ConversationResponse:
    try:
        return service.update_conversation(conversation_id, conversation_data)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{conversation_id}", response_model=DeleteResult)
def delete_conversation(
    conversation_id: int,
    service: ChatService = Depends(get_chat_service),
) -> DeleteResult:
    try:
        service.delete_conversation(conversation_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteResult(message="Conversation deleted successfully")
