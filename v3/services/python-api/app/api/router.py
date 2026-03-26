from fastapi import APIRouter

from app.api.routes.characters import router as characters_router
from app.api.routes.chat import router as chat_router
from app.api.routes.carmaker import router as carmaker_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.health import router as health_router
from app.api.routes.maps import router as maps_router
from app.api.routes.prompt_templates import router as prompt_templates_router
from app.api.routes.settings import router as settings_router
from app.api.routes.triggers import router as triggers_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(carmaker_router, prefix="/carmaker", tags=["carmaker"])
api_router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
api_router.include_router(characters_router, prefix="/characters", tags=["characters"])
api_router.include_router(prompt_templates_router, prefix="/prompt-templates", tags=["prompt_templates"])
api_router.include_router(maps_router, prefix="/maps", tags=["maps"])
