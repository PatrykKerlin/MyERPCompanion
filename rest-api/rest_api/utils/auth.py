from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, cast

from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from schemas.core import UserOutputSchema
from services.core import ModuleService, UserService
from utils.exceptions import InvalidCredentialsException, NoPermissionException, NotFoundException


class Auth:
    __pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    @classmethod
    async def authenticate(
        cls, session: AsyncSession, username: str, password: str, settings: Settings
    ) -> dict[str, str] | None:
        service = UserService()
        schema = await service.get_by_name(session, username)
        if not schema or not cls.__verify_password(password, cast(str, schema.password)):
            return None
        access_token = cls.create_access_token(schema.id, settings)
        refresh_token = cls.__create_refresh_token(schema.id, settings)
        return {"access": access_token, "refresh": refresh_token}

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.__pwd_context.hash(password)

    @classmethod
    def decode_access_token(cls, token: str, settings: Settings) -> dict[str, str | int]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            return {}

    @classmethod
    def create_access_token(cls, user_id: int, settings: Settings) -> str:
        time_to_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_type = "access"
        token = cls.__prepare_token(user_id, time_to_expire, token_type, settings)
        return token

    @classmethod
    async def validate_refresh_token(cls, session: AsyncSession, token: str, settings: Settings) -> UserOutputSchema:
        from services.core import UserService

        payload = cls.decode_access_token(token, settings)
        if payload.get("type") != "refresh":
            raise InvalidCredentialsException()
        user_id = payload.get("user", None)
        if not isinstance(user_id, int):
            raise InvalidCredentialsException()
        service = UserService()
        schema = await service.get_by_id(session, user_id)
        if not schema:
            raise InvalidCredentialsException()
        return schema

    @classmethod
    def restrict_access(cls) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(self: Any, *args: Any, request: Request, **kwargs: Any) -> Any:
                user_schema = request.state.user
                if not user_schema:
                    raise InvalidCredentialsException()
                if getattr(user_schema, "is_superuser", False):
                    return await func(self, *args, request=request, **kwargs)

                controller = self.__class__.__name__

                async with self._get_session() as session:
                    service = ModuleService()
                    module_schema = await service.get_by_controller(session, controller)

                if not module_schema:
                    raise NotFoundException()

                allowed_groups = {group.name for group in module_schema.groups}
                user_groups = {group.name for group in user_schema.groups}

                if not user_groups.intersection(allowed_groups):
                    raise NoPermissionException()

                return await func(self, *args, request=request, **kwargs)

            return wrapper

        return decorator

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
    def __prepare_token(
        cls,
        user_id: int,
        time_to_expire: timedelta,
        token_type: str,
        settings: Settings,
    ) -> str:
        token_data = {
            "user": user_id,
            "type": token_type,
            "exp": datetime.now(UTC) + time_to_expire,
        }
        encoded_jwt = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
