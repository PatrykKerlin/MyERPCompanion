from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from functools import wraps
from typing import Annotated, Any, Generic, TypeVar

from config.context import Context
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.params import Depends as DependsParam
from pydantic import ValidationError
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.param_schema import (
    FilterParamsSchema,
    IdsPayloadSchema,
    PaginatedResponseSchema,
    PaginationParamsSchema,
    SortingParamsSchema,
)
from services.base.base_service import BaseService
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import Auth
from utils.enums import Action, Permission
from utils.parsers import FilterParamsParser

TService = TypeVar("TService", bound=BaseService)
TInputSchema = TypeVar("TInputSchema", bound=BaseStrictSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BasePlainSchema)
TReturn = TypeVar("TReturn")


class BaseController(Generic[TService, TInputSchema, TOutputSchema]):
    _input_schema_cls: type[TInputSchema]
    _service_cls: type[TService]

    def __init__(self, context: Context, auth: Auth) -> None:
        self.router = APIRouter()
        self._get_session = context.get_session
        self._settings = context.settings
        self._logger = context.logger
        self._service = self._service_cls()
        self._auth = auth
        self._404_message = "{model} with ID {id} not found."
        self._default_actions = {
            Action.GET_ALL: True,
            Action.GET_ONE: True,
            Action.CREATE: True,
            Action.UPDATE: True,
            Action.DELETE: True,
        }

    @staticmethod
    def handle_exceptions(
        bulk: bool = False,
    ) -> Callable[[Callable[..., Awaitable[TReturn]]], Callable[..., Awaitable[TReturn]]]:
        def decorator(func: Callable[..., Awaitable[TReturn]]) -> Callable[..., Awaitable[TReturn]]:
            @wraps(func)
            async def wrapper(self: BaseController[Any, Any, Any], *args: Any, **kwargs: Any) -> TReturn:
                endpoint_name = f"{self.__class__.__name__}.{func.__qualname__}"
                try:
                    return await func(self, *args, **kwargs)
                except HTTPException:
                    self._logger.exception(f"HTTPException in {endpoint_name}")
                    raise
                except ValidationError as err:
                    self._logger.exception(f"ValidationError in {endpoint_name}")
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
                except NoResultFound as err:
                    self._logger.exception(f"NoResultFound in {endpoint_name}")
                    if bulk:
                        missing_id = str(err.args[0]) if err.args else "unknown"
                    else:
                        model_id = kwargs.get("model_id")
                        if model_id is None and len(args) > 1:
                            model_id = args[1]
                        missing_id = model_id if model_id is not None else "unknown"
                    detail = self._404_message.format(model=self._service._model_cls.__name__, id=missing_id)
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
                except SQLAlchemyError:
                    self._logger.exception(f"SQLAlchemyError in {endpoint_name}")
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT)

            return wrapper

        return decorator

    @handle_exceptions()
    async def get_all(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[TOutputSchema]:
        session = BaseController._get_request_session(request)
        offset, limit = BaseController._get_offset_and_limit(pagination)
        items, total = await self._service.get_all(
            session=session,
            filters=filters.filters,
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

    @handle_exceptions()
    async def get_by_id(self, request: Request, model_id: int) -> TOutputSchema:
        session = BaseController._get_request_session(request)
        return await self._service.get_one_by_id(session, model_id)

    @handle_exceptions()
    async def get_bulk(self, request: Request) -> list[TOutputSchema]:
        body = await request.json()
        payload = IdsPayloadSchema(**body)
        session = BaseController._get_request_session(request)
        return await self._service.get_many_by_ids(session, payload.ids)

    @handle_exceptions()
    async def create(self, request: Request) -> TOutputSchema:
        user = request.state.user
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Request body must be an object.",
            )
        schema = self._input_schema_cls(**body)
        session = BaseController._get_request_session(request)
        return await self._service.create(session, user.id, schema)

    @handle_exceptions()
    async def create_bulk(self, request: Request) -> list[TOutputSchema]:
        user = request.state.user
        body = await request.json()
        if not isinstance(body, list):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        schemas: list[TInputSchema] = []
        for item in body:
            if not isinstance(item, dict):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            schemas.append(self._input_schema_cls(**item))
        session = BaseController._get_request_session(request)
        return await self._service.create_bulk(session=session, created_by=user.id, schemas=schemas)

    @handle_exceptions()
    async def update(self, request: Request, model_id: int) -> TOutputSchema:
        user = request.state.user
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Request body must be an object.",
            )
        schema = self._input_schema_cls(**body)
        session = BaseController._get_request_session(request)
        return await self._service.update(session, model_id, user.id, schema)

    @handle_exceptions(bulk=True)
    async def update_bulk(self, request: Request) -> list[TOutputSchema]:
        user = request.state.user
        body = await request.json()
        if not isinstance(body, list):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        items: list[tuple[int, TInputSchema]] = []
        for item in body:
            if not isinstance(item, dict):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            model_id = item.get("id")
            if not isinstance(model_id, int):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            data = {key: value for key, value in item.items() if key != "id"}
            schema = self._input_schema_cls(**data)
            items.append((model_id, schema))
        session = BaseController._get_request_session(request)
        return await self._service.update_bulk(session=session, items=items, modified_by=user.id)

    @handle_exceptions()
    async def delete(self, request: Request, model_id: int) -> Response:
        user = request.state.user
        session = BaseController._get_request_session(request)
        await self._service.delete(session, model_id, user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @handle_exceptions(bulk=True)
    async def delete_bulk(self, request: Request) -> Response:
        user = request.state.user
        body = await request.json()
        payload = IdsPayloadSchema(**body)
        session = BaseController._get_request_session(request)
        await self._service.delete_bulk(session=session, model_ids=payload.ids, modified_by=user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _get_has_next_has_prev(offset: int, limit: int, total: int, page: int) -> tuple[bool, bool]:
        has_next = offset + limit < total
        has_prev = page > 1
        return has_next, has_prev

    @staticmethod
    def _get_offset_and_limit(pagination: PaginationParamsSchema) -> tuple[int, int]:
        offset = (pagination.page - 1) * pagination.page_size
        limit = pagination.page_size
        return offset, limit

    @staticmethod
    def _get_request_session(request: Request) -> AsyncSession:
        session = getattr(request.state, "db", None)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not initialized.",
            )
        return session

    def _register_routes(
        self,
        output_schema: type[TOutputSchema],
        include: Mapping[Action, bool] | None = None,
        path: str = "",
    ) -> None:
        id_param = "/{model_id:int}"
        mapping = self._default_actions if include is None else include
        if Action.GET_ALL in mapping:
            self.router.add_api_route(
                path=path,
                endpoint=self.get_all,
                methods=["GET"],
                response_model=PaginatedResponseSchema[output_schema],
                status_code=status.HTTP_200_OK,
                dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=mapping[Action.GET_ALL]),
            )
        if Action.GET_ONE in mapping:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.get_by_id,
                methods=["GET"],
                response_model=output_schema,
                status_code=status.HTTP_200_OK,
                dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=mapping[Action.GET_ONE]),
            )
        if Action.GET_BULK in mapping:
            self.router.add_api_route(
                path=path + "/get-bulk",
                endpoint=self.get_bulk,
                methods=["POST"],
                response_model=list[output_schema],
                status_code=status.HTTP_200_OK,
                dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=mapping[Action.GET_BULK]),
            )
        if Action.CREATE in mapping:
            self.router.add_api_route(
                path=path,
                endpoint=self.create,
                methods=["POST"],
                response_model=output_schema,
                status_code=status.HTTP_201_CREATED,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.CREATE]
                ),
            )
        if Action.CREATE_BULK in mapping:
            self.router.add_api_route(
                path=path + "/create-bulk",
                endpoint=self.create_bulk,
                methods=["POST"],
                response_model=list[output_schema],
                status_code=status.HTTP_201_CREATED,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.CREATE_BULK]
                ),
            )
        if Action.UPDATE_BULK in mapping:
            self.router.add_api_route(
                path=path + "/update-bulk",
                endpoint=self.update_bulk,
                methods=["PUT"],
                response_model=list[output_schema],
                status_code=status.HTTP_200_OK,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.UPDATE_BULK]
                ),
            )
        if Action.UPDATE in mapping:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.update,
                methods=["PUT"],
                response_model=output_schema,
                status_code=status.HTTP_200_OK,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.UPDATE]
                ),
            )
        if Action.DELETE_BULK in mapping:
            self.router.add_api_route(
                path=path + "/delete-bulk",
                endpoint=self.delete_bulk,
                methods=["DELETE"],
                status_code=status.HTTP_204_NO_CONTENT,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.DELETE_BULK]
                ),
            )
        if Action.DELETE in mapping:
            self.router.add_api_route(
                path=path + id_param,
                endpoint=self.delete,
                methods=["DELETE"],
                status_code=status.HTTP_204_NO_CONTENT,
                dependencies=self._restrict_access(
                    permissions=[Permission.CAN_READ, Permission.CAN_MODIFY], secured=mapping[Action.DELETE]
                ),
            )

    def _restrict_access(self, permissions: list[Permission], secured: bool) -> list[DependsParam]:
        if not secured:
            return []
        return [Depends(self._auth.restrict_access(permissions=permissions, controller=self.__class__.__name__))]
