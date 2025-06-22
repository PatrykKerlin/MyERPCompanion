from typing import Union

from fastapi import Request

from config import Context
from controllers.base import BaseController
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.core import UserService
from utils.auth import Auth
from utils.exceptions import NotFoundException


class UserController(
    BaseController[
        UserService,
        Union[UserInputCreateSchema, UserInputUpdateSchema],
        UserOutputSchema,
    ]
):
    _input_schema_cls = UserInputCreateSchema
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes(UserOutputSchema)

    @Auth.restrict_access()
    async def create(self, request: Request) -> UserOutputSchema:
        user = request.state.user
        body = await request.json()
        schema = UserInputCreateSchema(**body)
        async with self._get_session() as session:
            return await self._service.create(session, user.id, schema)

    @Auth.restrict_access()
    async def update(self, request: Request, model_id: int) -> UserOutputSchema:
        user = request.state.user
        body = await request.json()
        schema = UserInputUpdateSchema(**body)
        async with self._get_session() as session:
            schema = await self._service.update(session, model_id, user.id, schema)
            if not schema:
                raise NotFoundException()
            return schema
