from typing import Generic, List, NoReturn, Type, TypeVar

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from config import Context, Settings
from dtos.base import BaseDTO
from dtos.core import UserDTO
from schemas.base import BaseCreateSchema, BaseResponseSchema
from services.base import BaseService
from services.core import AuthService

TDTO = TypeVar("TDTO", bound=BaseDTO)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)
TResponseSchema = TypeVar("TResponseSchema", bound=BaseResponseSchema)
TService = TypeVar("TService", bound=BaseService)


class BaseController(Generic[TDTO, TCreateSchema, TResponseSchema, TService]):
    service: TService
    response_schema: Type[TResponseSchema]
    require_auth: bool = True
    required_groups: list[str] = []
    entity_name: str = "Entity"

    def __init__(self, context: Context) -> None:
        self.router = APIRouter()
        self._context = context

    async def _get_user_if_authorized(self, request: Request) -> UserDTO:
        async with self._context.get_db() as db:
            dto = await AuthService.get_user_if_authorized(
                db,
                self._context.settings,
                self._context.oauth2_scheme,
                request,
                self.__class__.required_groups,
            )
            return dto

    async def get_all(self, request: Request) -> List[TResponseSchema]:
        if self.__class__.require_auth:
            await self._get_user_if_authorized(request)
        async with self._context.get_db() as db:
            dtos = await self.__class__.service.get_all(db)
            return [self.__class__.response_schema(**dto.__dict__) for dto in dtos]

    async def get_by_id(self, request: Request, entity_id: int) -> TResponseSchema:
        if self.__class__.require_auth:
            await self._get_user_if_authorized(request)
        async with self._context.get_db() as db:
            dto = await self.__class__.service.get_by_id(db, entity_id)
            if not dto:
                self.__raise_not_found()
            return self.__class__.response_schema(**dto.__dict__)

    async def create(self, request: Request, data: TCreateSchema) -> TResponseSchema:
        user_dto = await self._get_user_if_authorized(request)
        async with self._context.get_db() as db:
            dto = await self.__class__.service.create(db, data, user_dto.id)
            return self.__class__.response_schema(**dto.__dict__)

    async def update(self, request: Request, entity_id: int, data: TCreateSchema) -> TResponseSchema:
        user_dto = await self._get_user_if_authorized(request)
        async with self._context.get_db() as db:
            dto = await self.__class__.service.update(db, entity_id, data, user_dto.id)
            if not dto:
                self.__raise_not_found()
            return self.__class__.response_schema(**dto.__dict__)

    async def delete(self, request: Request, entity_id: int) -> None:
        user_dto = await self._get_user_if_authorized(request)
        async with self._context.get_db() as db:
            success = await self.__class__.service.delete(db, entity_id, user_dto.id)
            if not success:
                self.__raise_not_found()
            return None

    def __raise_not_found(self) -> NoReturn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{self.__class__.entity_name} not found",
        )
