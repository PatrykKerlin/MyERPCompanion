from typing import Union

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Request, status
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateApiSchema, UserStrictUpdateApiSchema
from services.core import UserService
from utils.auth import Auth


class UserController(
    BaseController[UserService, Union[UserStrictCreateApiSchema, UserStrictUpdateApiSchema], UserPlainSchema]
):
    _input_schema_cls = UserStrictCreateApiSchema
    _service_cls = UserService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._register_routes(UserPlainSchema)
        self._service.set_auth(auth)

    @BaseController.handle_exceptions()
    async def create(self, request: Request) -> UserPlainSchema:
        user = request.state.user
        body = await request.json()
        schema = UserStrictCreateApiSchema(**body)
        session = BaseController._get_request_session(request)
        return await self._service.create(session, user.id, schema)

    @BaseController.handle_exceptions()
    async def update(self, request: Request, model_id: int) -> UserPlainSchema:
        user = request.state.user
        body = await request.json()
        schema = UserStrictUpdateApiSchema(**body)
        session = BaseController._get_request_session(request)
        return await self._service.update(session, model_id, user.id, schema)
