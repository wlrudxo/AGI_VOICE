from app.schemas.common import CamelModel


class ChatRequest(CamelModel):
    conversation_id: int | None = None
    character_id: int | None = None
    prompt_template_id: int | None = None
    user_info: str | None = None
    user_name: str | None = None
    final_message: str | None = None
    title: str | None = None
    message: str
    model: str = "sonnet"
    system_context: str | None = None
    role: str = "user"
    exclude_history: bool = False
    no_save: bool = False


class ChatResponse(CamelModel):
    conversation_id: int
    responses: list[str]
    actions: list[dict] = []
