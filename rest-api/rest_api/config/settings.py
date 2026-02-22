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
    CORS_ORIGINS: str | None = None
    DB_POOL_SIZE: int = 2
    DB_MAX_OVERFLOW: int = 1
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True
    ISSUER_NAME: str = ""
    ISSUER_TAX_ID: str = ""
    ISSUER_STREET: str = ""
    ISSUER_HOUSE_NUMBER: str = ""
    ISSUER_APARTMENT_NUMBER: str = ""
    ISSUER_POSTAL_CODE: str = ""
    ISSUER_CITY: str = ""
    ISSUER_COUNTRY: str = ""
    ISSUER_EMAIL: str = ""
    ISSUER_PHONE: str = ""
    ISSUER_BANK_NAME: str = ""
    ISSUER_BANK_ACCOUNT: str = ""

    model_config = {"env_file": ".env"}
