import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.services.settings import get_settings_service

settings = get_settings()


class QuietPollingAccessFilter(logging.Filter):
    _quiet_get_paths = (
        "/api/carmaker/telemetry",
        "/api/carmaker/status",
        "/api/carmaker/monitoring",
        "/api/settings/db/timestamp",
        "/api/triggers/events",
        "/api/triggers/logs",
        "/api/triggers/monitoring",
    )
    _quiet_any_method_paths = (
        "/api/carmaker/command",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        args = getattr(record, "args", ())
        if len(args) < 3:
            return True

        method = str(args[1])
        path = str(args[2])
        if method == "OPTIONS":
            return False

        if any(path.startswith(prefix) for prefix in self._quiet_any_method_paths):
            return False

        if method == "GET" and any(path.startswith(prefix) for prefix in self._quiet_get_paths):
            return False

        return True

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

logging.getLogger("uvicorn.access").addFilter(QuietPollingAccessFilter())


@app.on_event("startup")
async def startup_sync() -> None:
    try:
        result = get_settings_service().load_db_from_sync_folder_if_newer()
        if result:
            print(f"📥 {result}")
    except Exception as exc:
        print(f"⚠ Startup DB sync skipped: {exc}")


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
