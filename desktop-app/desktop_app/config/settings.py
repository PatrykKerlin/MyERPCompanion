from pydantic_settings import BaseSettings
from pydantic import Field
import locale


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    API_URL: str
    LANGUAGE: str = "pl"  # Field(default_factory=lambda: Settings.__get_system_language())
    THEME: str = "system"

    model_config = {"env_file": ".env"}

    # @staticmethod
    # def __get_system_language() -> str:
    #     lang, _ = locale.getlocale()
    #     if lang is None:
    #         return "en"
    #     return lang.split("_")[0]
