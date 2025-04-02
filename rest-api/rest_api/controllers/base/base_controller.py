from typing import Generic, TypeVar

from fastapi import APIRouter, Request, Response, status

from config import Context
from dtos.base import BaseDTO
from schemas.base import BaseCreateSchema, BaseResponseSchema
from services.base import BaseService
from utils.exceptions import NotFoundException, InvalidCredentialsException
from entities.base import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)
TDTO = TypeVar("TDTO", bound=BaseDTO)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)
TResponseSchema = TypeVar("TResponseSchema", bound=BaseResponseSchema)
TService = TypeVar("TService", bound=BaseService)


class BaseController(Generic[TDTO, TCreateSchema, TResponseSchema, TService]):
    _service: TService
    _response_schema: type[TResponseSchema]
    _entity: type[BaseEntity]
    _id_path = "/{entity_id}"

    def __init__(self, context: Context) -> None:
        self.router = APIRouter()
        self._context = context

    async def get_all(self, request: Request) -> list[TResponseSchema]:
        if not request.state.user:
            raise InvalidCredentialsException()
        async with self._context.get_db() as db:
            dtos = await self.__class__._service.get_all(db)
            return [self.__class__._response_schema(**dto.__dict__) for dto in dtos]

    async def get_by_id(self, request: Request, entity_id: int) -> TResponseSchema:
        async with self._context.get_db() as db:
            dto = await self.__class__._service.get_by_id(db, entity_id)
            if not dto:
                raise NotFoundException(self.__class__._entity_name)
            return self.__class__._response_schema(**dto.__dict__)

    async def create(self, request: Request, data: TCreateSchema) -> TResponseSchema:
        user_dto = request.state.user
        async with self._context.get_db() as db:
            dto = await self.__class__._service.create(db, user_dto.id, data)
            return self.__class__._response_schema(**dto.__dict__)

    async def update(
        self, request: Request, entity_id: int, data: TCreateSchema
    ) -> TResponseSchema:
        user_dto = request.state.user
        async with self._context.get_db() as db:
            dto = await self.__class__._service.update(db, entity_id, user_dto.id, data)
            if not dto:
                raise NotFoundException(self.__class__._entity_name)
            return self.__class__._response_schema(**dto.__dict__)

    async def delete(self, request: Request, entity_id: int) -> Response:
        user_dto = request.state.user
        async with self._context.get_db() as db:
            success = await self.__class__._service.delete(db, entity_id, user_dto.id)
            if not success:
                raise NotFoundException(self._entity.__name__)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    def _register_routes(self, methods: list[str], prefix: str = "") -> None:
        if "GET_ALL" in methods:
            self.router.add_api_route(
                path=prefix,
                endpoint=self.get_all,
                methods=["GET"],
                response_model=list[self._response_schema],
                status_code=status.HTTP_200_OK
            )
        if "GET_ONE" in methods:
            self.router.add_api_route(
                path=prefix + self._id_path,
                endpoint=self.get_by_id,
                methods=["GET"],
                response_model=self._response_schema,
                status_code=status.HTTP_200_OK
            )
        if "POST" in methods:
            self.router.add_api_route(
                path=prefix,
                endpoint=self.create,
                methods=["POST"],
                response_model=self._response_schema,
                status_code=status.HTTP_201_CREATED
            )
        if "PUT" in methods:
            self.router.add_api_route(
                path=prefix + self._id_path,
                endpoint=self.update,
                methods=["PUT"],
                response_model=self._response_schema,
                status_code=status.HTTP_200_OK
            )
        if "DELETE" in methods:
            self.router.add_api_route(
                path=prefix + self._id_path,
                endpoint=self.delete,
                methods=["DELETE"],
                status_code=status.HTTP_204_NO_CONTENT
            )
