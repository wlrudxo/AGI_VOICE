from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AGI Voice V3 Python API"
    app_version: str = "0.1.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:4173"]
    data_dir: str = ".data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def data_dir_path(self) -> Path:
        return Path(self.data_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
