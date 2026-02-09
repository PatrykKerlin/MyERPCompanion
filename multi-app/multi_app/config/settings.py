import locale
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_URL: str
    PUBLIC_API_URL: str | None = None
    CLIENT: Literal["desktop", "mobile"]
    LANGUAGE: str = Field(default_factory=lambda: Settings.__get_system_language())
    THEME: str = "system"
    API_CHECK_DELAY: int = 60
    TIMEZONE: str | None = None

    model_config = {"env_file": ".env"}

    @staticmethod
    def __get_system_language() -> str:
        lang, _ = locale.getlocale()
        if lang is None:
            return "en"
        return lang.split("_")[0]
