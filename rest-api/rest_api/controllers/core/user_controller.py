from typing import Union

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from config import Context
from controllers.base import BaseController
from schemas.core import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema
from services.core import UserService
from utils.auth import Auth


class UserController(
    BaseController[
        UserService,
        Union[UserStrictCreateSchema, UserStrictUpdateSchema],
        UserPlainSchema,
    ]
):
    _input_schema_cls = UserStrictCreateSchema
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes(UserPlainSchema)

    @Auth.restrict_access()
    async def create(self, request: Request) -> UserPlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            schema = UserStrictCreateSchema(**body)
            async with self._get_session() as session:
                return await self._service.create(session, user.id, schema)
        except HTTPException:
            raise
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    @Auth.restrict_access()
    async def update(self, request: Request, model_id: int) -> UserPlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            schema = UserStrictUpdateSchema(**body)
            async with self._get_session() as session:
                schema = await self._service.update(session, model_id, user.id, schema)
                if not schema:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
                    )
                return schema
        except HTTPException:
            raise
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
