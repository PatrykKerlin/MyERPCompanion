from typing import Generic, Literal, TypeVar

from fastapi import APIRouter, Request, Response, status

from config import Context
from schemas.base import BaseCreateSchema, BaseResponseSchema
from services.base import BaseService
from utils.exceptions import NotFoundException

TService = TypeVar("TService", bound=BaseService)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)
TResponseSchema = TypeVar("TResponseSchema", bound=BaseResponseSchema)


class BaseController(Generic[TService, TCreateSchema, TResponseSchema]):
    _service_cls: type[TService]

    def __init__(self, context: Context) -> None:
        self.router = APIRouter()
        self._get_session = context.get_session
        self._settings = context.settings
        self._service = self._service_cls()

    async def get_all(self, _: Request) -> list[TResponseSchema]:
        async with self._get_session() as session:
            return await self._service.get_all(session)

    async def get_by_id(self, _: Request, entity_id: int) -> TResponseSchema:
        async with self._get_session() as session:
            schema = await self._service.get_by_id(session, entity_id)
            if not schema:
                raise NotFoundException()
            return schema

    async def create(self, data: TCreateSchema, request: Request) -> TResponseSchema:
        user = request.state.user
        async with self._get_session() as session:
            return await self._service.create(session, user.id, data)

    async def update(
        self, data: TCreateSchema, request: Request, entity_id: int
    ) -> TResponseSchema:
        user = request.state.user
        async with self._get_session() as session:
            schema = await self._service.update(session, entity_id, user.id, data)
            if not schema:
                raise NotFoundException()
            return schema

    async def delete(self, request: Request, entity_id: int) -> Response:
        user = request.state.user
        async with self._get_session() as session:
            success = await self._service.delete(session, entity_id, user.id)
            if not success:
                raise NotFoundException()
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    def _register_routes(
        self,
        path: str,
        id_param: str,
        response_schema: type[TResponseSchema],
        include: (
            list[Literal["get_all", "get_by_id", "create", "update", "delete"]] | None
        ) = None,
    ) -> None:
        include = (
            include
            if include
            else ["get_all", "get_by_id", "create", "update", "delete"]
        )
        if "get_all" in include:
            self.router.add_api_route(
                path=path,
                endpoint=self.get_all,
                methods=["GET"],
                response_model=list[response_schema],
                status_code=status.HTTP_200_OK,
            )
        if "get_by_id" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.get_by_id,
                methods=["GET"],
                response_model=response_schema,
                status_code=status.HTTP_200_OK,
            )
        if "create" in include:
            self.router.add_api_route(
                path=path,
                endpoint=self.create,
                methods=["POST"],
                response_model=response_schema,
                status_code=status.HTTP_201_CREATED,
            )
        if "update" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.update,
                methods=["PUT"],
                response_model=response_schema,
                status_code=status.HTTP_200_OK,
            )
        if "delete" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.delete,
                methods=["DELETE"],
                status_code=status.HTTP_204_NO_CONTENT,
            )
