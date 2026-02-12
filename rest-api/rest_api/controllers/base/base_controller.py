from collections.abc import Mapping
from typing import Annotated, Generic, TypeVar

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

    async def create(self, request: Request) -> TOutputSchema:
        try:
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
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.create.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.create.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.create.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def create_bulk(self, request: Request) -> list[TOutputSchema]:
        try:
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
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.create_bulk.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.create_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.create_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def delete(self, request: Request, model_id: int) -> Response:
        try:
            user = request.state.user
            session = BaseController._get_request_session(request)
            await self._service.delete(session, model_id, user.id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.delete.__qualname__}")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.delete.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.delete.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def delete_bulk(self, request: Request) -> Response:
        try:
            user = request.state.user
            body = await request.json()
            payload = IdsPayloadSchema(**body)
            session = BaseController._get_request_session(request)
            await self._service.delete_bulk(session=session, model_ids=payload.ids, modified_by=user.id)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.delete_bulk.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.delete_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except NoResultFound as err:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.delete_bulk.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=str(err.args[0])),
            )
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.delete_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def get_all(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[TOutputSchema]:
        try:
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
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_all.__qualname__}")
            raise
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_all.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def get_bulk(self, request: Request) -> list[TOutputSchema]:
        try:
            body = await request.json()
            payload = IdsPayloadSchema(**body)
            session = BaseController._get_request_session(request)
            return await self._service.get_many_by_ids(session, payload.ids)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_bulk.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.get_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def get_by_id(self, request: Request, model_id: int) -> TOutputSchema:
        try:
            session = BaseController._get_request_session(request)
            return await self._service.get_one_by_id(session, model_id)
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_by_id.__qualname__}")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.get_by_id.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_by_id.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def update(self, request: Request, model_id: int) -> TOutputSchema:
        try:
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
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.update.__qualname__}")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.update.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def update_bulk(self, request: Request) -> list[TOutputSchema]:
        try:
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
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.update_bulk.__qualname__}")
            raise
        except ValidationError as err:
            self._logger.exception(f"ValidationError in {self.__class__.__name__}.{self.update_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except NoResultFound as err:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.{self.update_bulk.__qualname__}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=str(err.args[0])),
            )
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.update_bulk.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

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
