from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    API_URL: str
    LANGUAGE: str = "en"
    THEME: str = "dark"

    model_config = {"env_file": ".env"}
