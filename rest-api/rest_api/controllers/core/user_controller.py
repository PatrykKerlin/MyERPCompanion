from typing import Union

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from config.context import Context
from controllers.base.base_controller import BaseController
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema
from services.core import UserService
from utils.auth import Auth


class UserController(
    BaseController[UserService, Union[UserStrictCreateSchema, UserStrictUpdateSchema], UserPlainSchema]
):
    _input_schema_cls = UserStrictCreateSchema
    _service_cls = UserService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._register_routes(UserPlainSchema)
        self._service.set_auth(auth)

    async def create(self, request: Request) -> UserPlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            schema = UserStrictCreateSchema(**body)
            session = BaseController._get_request_session(request)
            return await self._service.create(session, user.id, schema)
        except HTTPException:
            raise
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def update(self, request: Request, model_id: int) -> UserPlainSchema:
        try:
            user = request.state.user
            body = await request.json()
            schema = UserStrictUpdateSchema(**body)
            session = BaseController._get_request_session(request)
            return await self._service.update(session, model_id, user.id, schema)
        except HTTPException:
            raise
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._404_message.format(model=self._service._model_cls.__name__, id=model_id),
            )
        except ValidationError as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.errors())
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
