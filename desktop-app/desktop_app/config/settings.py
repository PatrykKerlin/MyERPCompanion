from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_URL: str

    model_config = {"env_file": ".env"}
