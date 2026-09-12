from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    backend_url: str = Field(default="http://backend:8000", alias="BACKEND_URL")
    default_group: str = Field(default="РЗ-252", alias="DEFAULT_GROUP")
