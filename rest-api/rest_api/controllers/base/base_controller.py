from typing import Annotated, Generic, Literal, TypeVar

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import String
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from config import Context
from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import FilterParamsSchema, PaginatedResponseSchema, PaginationParamsSchema, SortingParamsSchema
from services.base import BaseService
from utils.auth import Auth
from utils.exceptions import NotFoundException
from utils.parsers import FilterParamsParser

TService = TypeVar("TService", bound=BaseService)
TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseController(Generic[TService, TInputSchema, TOutputSchema]):
    _input_schema_cls: type[TInputSchema]
    _service_cls: type[TService]

    def __init__(self, context: Context) -> None:
        self.router = APIRouter()
        self._get_session = context.get_session
        self._settings = context.settings
        self._service = self._service_cls()

    @Auth.restrict_access()
    async def get_all(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[TOutputSchema]:
        async with self._get_session() as session:
            conditions: list[ColumnElement[bool]] = []
            for key, value in filters.filters.items():
                attr = getattr(self._service._model_cls, key, None)
                if isinstance(attr, InstrumentedAttribute):
                    if hasattr(attr, "property") and isinstance(attr.property.columns[0].type, String):
                        conditions.append(attr.ilike(f"%{value}%"))
                    else:
                        conditions.append(attr == value)

            offset, limit = BaseController._get_offset_and_limit(pagination)
            items, total = await self._service.get_all(
                session=session,
                filters=conditions,
                offset=offset,
                limit=limit,
                sort_by=sorting.sort_by,
                sort_order=sorting.order,
            )
            has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)

            return PaginatedResponseSchema[TOutputSchema](
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                has_next=has_next,
                has_prev=has_prev,
            )

    @Auth.restrict_access()
    async def get_by_id(self, request: Request, model_id: int) -> TOutputSchema:
        async with self._get_session() as session:
            schema = await self._service.get_one_by_id(session, model_id)
            if not schema:
                raise NotFoundException()
            return schema

    @Auth.restrict_access()
    async def create(self, request: Request) -> TOutputSchema:
        user = request.state.user
        body = await request.json()
        schema = self._input_schema_cls(**body)
        async with self._get_session() as session:
            return await self._service.create(session, user.id, schema)

    @Auth.restrict_access()
    async def update(self, request: Request, model_id: int) -> TOutputSchema:
        user = request.state.user
        body = await request.json()
        schema = self._input_schema_cls(**body)
        async with self._get_session() as session:
            schema = await self._service.update(session, model_id, user.id, schema)
            if not schema:
                raise NotFoundException()
            return schema

    @Auth.restrict_access()
    async def delete(self, request: Request, model_id: int) -> Response:
        user = request.state.user
        async with self._get_session() as session:
            success = await self._service.delete(session, model_id, user.id)
            if not success:
                raise NotFoundException()
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    def _register_routes(
        self,
        output_schema: type[TOutputSchema],
        include: list[Literal["get_all", "get_by_id", "create", "update", "delete"]] | None = None,
        path: str = "",
    ) -> None:
        id_param = "/{model_id}"
        include = include if include else ["get_all", "get_by_id", "create", "update", "delete"]
        if "get_all" in include:
            self.router.add_api_route(
                path=path,
                endpoint=self.get_all,
                methods=["GET"],
                response_model=PaginatedResponseSchema[output_schema],
                status_code=status.HTTP_200_OK,
            )
        if "get_by_id" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.get_by_id,
                methods=["GET"],
                response_model=output_schema,
                status_code=status.HTTP_200_OK,
            )
        if "create" in include:
            self.router.add_api_route(
                path=path,
                endpoint=self.create,
                methods=["POST"],
                response_model=output_schema,
                status_code=status.HTTP_201_CREATED,
            )
        if "update" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.update,
                methods=["PUT"],
                response_model=output_schema,
                status_code=status.HTTP_200_OK,
            )
        if "delete" in include:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.delete,
                methods=["DELETE"],
                status_code=status.HTTP_204_NO_CONTENT,
            )

    @staticmethod
    def _get_offset_and_limit(pagination: PaginationParamsSchema) -> tuple[int, int]:
        offset = (pagination.page - 1) * pagination.page_size
        limit = pagination.page_size
        return offset, limit

    @staticmethod
    def _get_has_next_has_prev(offset: int, limit: int, total: int, page: int) -> tuple[bool, bool]:
        has_next = offset + limit < total
        has_prev = page > 1
        return has_next, has_prev
