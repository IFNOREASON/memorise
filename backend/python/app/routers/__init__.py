from app.routers.health import router as health_router
from app.routers.config import router as config_router
from app.routers.photos import router as photos_router
from app.routers.avatars import router as avatars_router
from app.routers.memories import router as memories_router
from app.routers.voice import router as voice_router
from app.routers.chat import router as chat_router

__all__ = [
    "health_router",
    "config_router",
    "photos_router",
    "avatars_router",
    "memories_router",
    "voice_router",
    "chat_router"
]
