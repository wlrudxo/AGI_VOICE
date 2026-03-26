from app.schemas.common import CamelModel


class ConversationResponse(CamelModel):
    id: int
    character_id: int
    prompt_template_id: int
    user_info: str | None = None
    title: str | None = None
    created_at: str
    updated_at: str


class ConversationWithCount(ConversationResponse):
    message_count: int


class MessageResponse(CamelModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str


class ConversationUpdate(CamelModel):
    title: str | None = None
    user_info: str | None = None


class DeleteResult(CamelModel):
    message: str
