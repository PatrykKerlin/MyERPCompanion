from typing import Callable, List

from fastapi import status, Request

from config import Context
from controllers.base import BaseController
from entities.core import User
from schemas.core import UserResponse
from services.core import UserService
from utils.exceptions import InvalidCredentialsException


class UserController(BaseController):
    _service = UserService()
    _response_schema = UserResponse
    _entity = User

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=self._response_schema,
            status_code=status.HTTP_200_OK
        )
        self._register_routes(["GET_ALL", "GET_ONE", "POST", "PUT", "DELETE"])

    @classmethod
    async def current_user(cls, request: Request) -> UserResponse:
        user_dto = request.state.user
        if not user_dto:
            raise InvalidCredentialsException()
        return UserResponse(**user_dto.__dict__)
