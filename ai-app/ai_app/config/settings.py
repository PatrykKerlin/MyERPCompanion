from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TIMEZONE: str = "UTC"
    TRAIN_HOUR_UTC: int = 0
    TRAIN_MINUTE_UTC: int = 0

    model_config = {"env_file": ".env"}
