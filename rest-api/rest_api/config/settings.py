from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    MODULE_HEADER: str
    MEDIA_DIR: str
    MEDIA_URL: str

    model_config = {"env_file": ".env"}
