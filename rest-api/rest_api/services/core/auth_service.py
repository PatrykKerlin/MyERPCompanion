from datetime import UTC, datetime, timedelta
from typing import NoReturn, cast

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from repositories.core import UserRepository
from dtos.core import UserDTO
from utils.exceptions import InvalidCredentialsException


class AuthService:
    __pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    @classmethod
    async def authenticate(
        cls, db: AsyncSession, username: str, password: str, settings: Settings
    ) -> dict[str, str] | None:
        user = await UserRepository.get_by_name(db, username)
        if not user or not cls.__verify_password(password, cast(str, user.password)):
            return None
        access_token = cls.create_access_token(user.id, settings)
        refresh_token = cls.__create_refresh_token(user.id, settings)
        return {"access_token": access_token, "refresh_token": refresh_token}

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.__pwd_context.hash(password)

    @classmethod
    def decode_access_token(cls, token: str, settings: Settings) -> dict[str, str | int]:
        try:
            return jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            return {}

    @classmethod
    def create_access_token(cls, user_id: int, settings: Settings) -> str:
        time_to_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_type = "access"
        token = cls.__prepare_token(user_id, time_to_expire, token_type, settings)
        return token

    @classmethod
    async def validate_refresh_token(cls, token: str, settings: Settings) -> UserDTO:
        from services.core import UserService
        payload = cls.decode_access_token(token, settings)
        if payload.get("type") != "refresh":
            raise InvalidCredentialsException()
        user_id = payload.get("user")
        iat = payload.get("iat")
        user_dto = await UserService.get_by_id(user_id)
        if not user_dto or not iat or datetime.fromtimestamp(iat, UTC) < user_dto.pwd_modified_at:
            raise InvalidCredentialsException()
        return user_dto

    @classmethod
    def __verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.__pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def __create_refresh_token(cls, user_id: int, settings: Settings) -> str:
        time_to_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_type = "refresh"
        token = cls.__prepare_token(user_id, time_to_expire, token_type, settings)
        return token

    @classmethod
    def __prepare_token(cls, user_id: int, time_to_expire: timedelta,
                        token_type: str, settings: Settings) -> str:
        expiration_time = datetime.now(UTC) + time_to_expire
        token_data = {
            "user": user_id,
            "type": token_type,
            "iat": int(datetime.now(UTC).timestamp()),
            "exp": expiration_time
        }
        encoded_jwt = jwt.encode(
            token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
