from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TIMEZONE: str = "UTC"
    TRAIN_HOUR_UTC: int = 0
    TRAIN_MINUTE_UTC: int = 0
    FORECAST_HORIZON_MONTHS: int = 6
    FORECAST_DISCOUNT_SCENARIOS: list[float] = [0.00, 0.05, 0.10, 0.15, 0.20]
    DB_POOL_SIZE: int = 2
    DB_MAX_OVERFLOW: int = 1
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True

    model_config = {"env_file": ".env"}
