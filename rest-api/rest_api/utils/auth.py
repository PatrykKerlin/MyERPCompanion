from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Awaitable, cast

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import exists, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from config import Context
from utils.enums import Permission
from models.core import AssocUserView
from schemas.core import UserPlainSchema
from services.core import ModuleService, UserService


class Auth:
    def __init__(self, context: Context) -> None:
        self.__get_session = context.get_session
        self.__settings = context.settings
        self.__pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.__user_service = UserService()
        self.__user_service.set_auth(self)

    async def authenticate(self, session: AsyncSession, username: str, password: str) -> dict[str, str] | None:
        user_schema = await self.__user_service.get_one_by_username(session, username)
        if not user_schema or not self.__verify_password(password, cast(str, user_schema.password)):
            return None
        access_token = self.create_access_token(user_schema.id)
        refresh_token = self.__create_refresh_token(user_schema.id)
        return {"access": access_token, "refresh": refresh_token}

    def get_password_hash(self, password: str) -> str:
        return self.__pwd_context.hash(password)

    def decode_access_token(self, token: str) -> dict[str, str | int]:
        try:
            return jwt.decode(token, self.__settings.SECRET_KEY, algorithms=[self.__settings.ALGORITHM])
        except JWTError:
            return {}

    def create_access_token(
        self,
        user_id: int,
    ) -> str:
        time_to_expire = timedelta(minutes=self.__settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_type = "access"
        token = self.__prepare_token(user_id, time_to_expire, token_type)
        return token

    async def validate_refresh_token(self, session: AsyncSession, token: str) -> UserPlainSchema:
        payload = self.decode_access_token(token)
        user_id = payload.get("user")
        token_type = payload.get("type")
        if not isinstance(user_id, int) or token_type != "refresh":
            raise NoResultFound()
        user_schema = await self.__user_service.get_one_by_id(session, user_id)
        if not user_schema:
            raise NoResultFound()
        return user_schema

    def restrict_access(self, permissions: list[Permission], controller: str) -> Callable[..., Awaitable[None]]:
        async def dependency(request: Request) -> None:
            user_schema = getattr(request.state, "user", None)
            if not user_schema:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            if user_schema and user_schema.is_superuser:
                return
            view_schema = getattr(request.state, "view", None)
            if not view_schema:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            if not view_schema or controller not in set(view_schema.controllers):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            async with self.__get_session() as session:
                module_service = ModuleService()
                module_schema = await module_service.get_one_by_id(session, view_schema.module_id)
                if not module_schema:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

                allowed_groups = {group.key for group in module_schema.groups}
                user_groups = {group.key for group in user_schema.groups}

                if not user_groups.intersection(allowed_groups):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

                permission_columns = [getattr(AssocUserView, permission) for permission in permissions]

                has_permission = await session.scalar(
                    select(
                        exists().where(
                            AssocUserView.is_active.is_(True),
                            AssocUserView.user_id == user_schema.id,
                            AssocUserView.view_id == view_schema.id,
                            *[column.is_(True) for column in permission_columns],
                        )
                    )
                )

                if not has_permission:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return dependency

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.__pwd_context.verify(plain_password, hashed_password)

    def __create_refresh_token(self, user_id: int) -> str:
        time_to_expire = timedelta(days=self.__settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_type = "refresh"
        token = self.__prepare_token(user_id, time_to_expire, token_type)
        return token

    def __prepare_token(self, user_id: int, time_to_expire: timedelta, token_type: str) -> str:
        token_data = {
            "user": user_id,
            "type": token_type,
            "exp": datetime.now(UTC) + time_to_expire,
        }
        encoded_jwt = jwt.encode(token_data, self.__settings.SECRET_KEY, algorithm=self.__settings.ALGORITHM)
        return encoded_jwt
