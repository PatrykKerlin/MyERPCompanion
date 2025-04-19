# pyright: reportIncompatibleMethodOverride=false

from typing import Union

from fastapi import Request, status

from config import Context
from controllers.base import BaseController
from schemas.core import UserCreate, UserResponse, UserUpdate
from services.core import UserService
from utils.exceptions import InvalidCredentialsException


class UserController(
    BaseController[UserService, Union[UserCreate, UserUpdate], UserResponse]
):
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes(UserResponse)
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserResponse,
            status_code=status.HTTP_200_OK,
        )

    @classmethod
    async def current_user(cls, request: Request) -> UserResponse:
        user_internal = request.state.user
        if not user_internal:
            raise InvalidCredentialsException()
        return UserResponse.model_construct(**user_internal.model_dump())
