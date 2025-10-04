from __future__ import annotations
from typing import Union, TYPE_CHECKING

from fastapi import APIRouter, Request, status, HTTPException

from schemas.core import UserPlainSchema
from controllers.base import BaseController
from utils.enums import Permission
from services.core import UserService
from schemas.core import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema

if TYPE_CHECKING:
    from config import Context
    from utils.auth import Auth


class CurrentUserController(
    BaseController[UserService, Union[UserStrictCreateSchema, UserStrictUpdateSchema], UserPlainSchema]
):
    _input_schema_cls = UserStrictCreateSchema
    _service_cls = UserService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._service.set_auth(auth)
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserPlainSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )

    async def current_user(self, request: Request) -> UserPlainSchema:
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user
