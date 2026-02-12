import asyncio
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Awaitable, cast

from config.context import Context
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from models.core.assoc_module_group import AssocModuleGroup
from passlib.context import CryptContext
from schemas.core.user_schema import UserPlainSchema
from services.business.logistic import WarehouseService
from services.core import ModuleService, UserService
from sqlalchemy import exists, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from utils.enums import Permission


class Auth:
    def __init__(self, context: Context) -> None:
        self.__settings = context.settings
        self.__pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.__user_service = UserService()
        self.__user_service.set_auth(self)
        self.__module_service = ModuleService()
        self.__warehouse_service = WarehouseService()

    async def authenticate(
        self,
        session: AsyncSession,
        username: str,
        password: str,
        client: str,
        warehouse_id: int | None = None,
    ) -> tuple[dict[str, str] | None, str | None]:
        user_schema = await self.__user_service.get_one_by_username(session, username)
        if not user_schema or not await self.__verify_password(password, cast(str, user_schema.password)):
            return None, "invalid_credentials"
        is_superuser = user_schema.is_superuser
        has_employee = user_schema.employee_id is not None
        has_customer = user_schema.customer_id is not None
        effective_warehouse_id: int | None = None
        if client in {"desktop", "mobile"}:
            allowed = is_superuser or has_employee
        elif client == "web":
            allowed = is_superuser or has_customer
        else:
            return None, "invalid_client"
        if not allowed:
            return None, "user_not_allowed"
        if client == "mobile":
            if user_schema.warehouse_id is not None:
                effective_warehouse_id = user_schema.warehouse_id
            elif warehouse_id is None:
                return None, "warehouse_required"
            else:
                try:
                    selected_warehouse = await self.__warehouse_service.get_one_by_id(session, warehouse_id)
                except NoResultFound:
                    return None, "invalid_warehouse"
                effective_warehouse_id = selected_warehouse.id
        access_token = self.create_access_token(
            user_schema.id,
            client=client,
            warehouse_id=effective_warehouse_id,
        )
        refresh_token = self.__create_refresh_token(
            user_schema.id,
            client=client,
            warehouse_id=effective_warehouse_id,
        )
        return {"access": access_token, "refresh": refresh_token}, None

    async def get_password_hash(self, password: str) -> str:
        return await asyncio.to_thread(self.__pwd_context.hash, password)

    def decode_access_token(self, token: str) -> dict[str, str | int]:
        try:
            return jwt.decode(token, self.__settings.SECRET_KEY, algorithms=[self.__settings.ALGORITHM])
        except JWTError:
            return {}

    def create_access_token(
        self,
        user_id: int,
        client: str | None = None,
        warehouse_id: int | None = None,
    ) -> str:
        time_to_expire = timedelta(minutes=self.__settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_type = "access"
        token = self.__prepare_token(
            user_id,
            time_to_expire,
            token_type,
            client=client,
            warehouse_id=warehouse_id,
        )
        return token

    async def validate_refresh_token(
        self, session: AsyncSession, token: str, client: str | None
    ) -> tuple[UserPlainSchema, str | None, int | None]:
        payload = self.decode_access_token(token)
        user_id = payload.get("user")
        token_type = payload.get("type")
        token_client = payload.get("client")
        token_warehouse_id = payload.get("warehouse_id")
        if not isinstance(user_id, int) or token_type != "refresh":
            raise NoResultFound()
        if token_client is not None and token_client != client:
            raise NoResultFound()
        user_schema = await self.__user_service.get_one_by_id(session, user_id)
        if not user_schema:
            raise NoResultFound()
        return (
            user_schema,
            token_client if isinstance(token_client, str) else None,
            token_warehouse_id if isinstance(token_warehouse_id, int) else None,
        )

    def restrict_access(self, permissions: list[Permission], controller: str) -> Callable[..., Awaitable[None]]:
        async def dependency(request: Request) -> None:
            user_schema = getattr(request.state, "user", None)
            if not user_schema:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            if user_schema and user_schema.is_superuser:
                return

            module_schema = getattr(request.state, "module", None)
            if not module_schema:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            if not module_schema or controller not in set(module_schema.controllers):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

            async def check_permissions(session: AsyncSession) -> None:
                refreshed_module = await self.__module_service.get_one_by_id(session, module_schema.id)
                if not refreshed_module:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

                allowed_groups = {group.id for group in refreshed_module.groups}
                user_groups = {group.id for group in user_schema.groups}
                common_groups = user_groups.intersection(allowed_groups)

                if not common_groups:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

                permission_columns = [getattr(AssocModuleGroup, permission) for permission in permissions]

                has_permission = await session.scalar(
                    select(
                        exists().where(
                            AssocModuleGroup.is_active.is_(True),
                            AssocModuleGroup.group_id.in_(common_groups),
                            AssocModuleGroup.module_id == refreshed_module.id,
                            *[column.is_(True) for column in permission_columns],
                        )
                    )
                )

                if not has_permission:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

            session = getattr(request.state, "db", None)
            if session is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            await check_permissions(session)

        return dependency

    async def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return await asyncio.to_thread(self.__pwd_context.verify, plain_password, hashed_password)

    def __create_refresh_token(
        self,
        user_id: int,
        client: str | None = None,
        warehouse_id: int | None = None,
    ) -> str:
        time_to_expire = timedelta(days=self.__settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_type = "refresh"
        token = self.__prepare_token(
            user_id,
            time_to_expire,
            token_type,
            client=client,
            warehouse_id=warehouse_id,
        )
        return token

    def __prepare_token(
        self,
        user_id: int,
        time_to_expire: timedelta,
        token_type: str,
        client: str | None,
        warehouse_id: int | None = None,
    ) -> str:
        token_data = {
            "user": user_id,
            "type": token_type,
            "exp": datetime.now(UTC) + time_to_expire,
        }
        if client:
            token_data["client"] = client
        if warehouse_id is not None:
            token_data["warehouse_id"] = warehouse_id
        encoded_jwt = jwt.encode(token_data, self.__settings.SECRET_KEY, algorithm=self.__settings.ALGORITHM)
        return encoded_jwt
