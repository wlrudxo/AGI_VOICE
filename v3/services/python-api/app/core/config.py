import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AGI Voice V3 Python API"
    app_version: str = "0.1.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:4173"]
    data_dir: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def data_dir_path(self) -> Path:
        if self.data_dir:
            return Path(self.data_dir)

        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "AGI_VOICE_V3"

        return Path.home() / ".local" / "share" / "AGI_VOICE_V3"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
