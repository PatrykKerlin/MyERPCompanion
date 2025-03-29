from datetime import UTC, datetime, timedelta
from typing import NoReturn, cast

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from dtos.core import UserDTO
from repositories.core import UserRepository
from utils.exceptions import InvalidCredentialsException, NoPermissionException


class AuthService:
    __pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    # __settings: Settings
    #
    # @classmethod
    # def set_settings(cls, settings: Settings) -> None:
    #     cls.__settings = settings

    @classmethod
    async def authenticate(
        cls, db: AsyncSession, username: str, password: str, settings: Settings
    ) -> dict[str, str] | None:
        user = await UserRepository.get_by_name(db, username)
        if not user or not cls.__verify_password(password, cast(str, user.password)):
            return None
        token_data = {
            "user": user.id,
            "iat": int(datetime.now(UTC).timestamp())
        }
        access_token = __create_access_token(token_data, settings)
        refresh_token = __create_refresh_token(token_data, settings)
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
    async def get_user_if_authorized(
        cls,
        db: AsyncSession,
        settings: Settings,
        oauth2_scheme: OAuth2PasswordBearer,
        request: Request,
        required_groups: list[str],
    ) -> UserDTO:
        token = await oauth2_scheme(request)
        if not token:
            raise InvalidCredentialsException()
        payload = cls.decode_access_token(token, settings)
        if not payload or "user" not in payload or "iat" not in payload:
            raise InvalidCredentialsException()
        user_id = payload["user"]
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise InvalidCredentialsException()
        iat = payload["iat"]
        if datetime.fromtimestamp(iat, UTC) < user.pwd_changed_at:
            raise InvalidCredentialsException()
        if not (
            user.is_superuser
            or any(group.name in required_groups for group in user.groups)
        ):
            raise NoPermissionException()
        dto = UserDTO.from_entity(user)
        return cast(UserDTO, dto)

    @classmethod
    def __verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.__pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def __create_access_token(cls, token_data: dict[str, str | int], settings: Settings) -> str:
        time_to_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_type = "access"
        token = cls.__prepare_token(token_data, time_to_expire, token_type, settings)
        return token

    @classmethod
    def __create_refresh_token(cls, token_data: dict[str, str | int], settings: Settings) -> str:
        time_to_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_type = "refresh"
        token = cls.__prepare_token(token_data, time_to_expire, token_type, settings)
        return token

    @classmethod
    def __prepare_token(cls, token_data: dict[str, str | int], time_to_expire: timedelta,
                        token_type: str, settings: Settings) -> str:
        expiration_time = datetime.now(UTC) + time_to_expire
        token_data.update({
            "type": token_type,
            "exp": expiration_time
        })
        encoded_jwt = jwt.encode(
            token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
