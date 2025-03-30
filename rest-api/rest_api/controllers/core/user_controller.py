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
            "/current-user", self.current_user, methods=["GET"], response_model=UserResponse
        )
        self.router.add_api_route(
            "", self.get_all, methods=["GET"], response_model=List[UserResponse]
        )
        self.router.add_api_route(
            self._id_path, self.get_by_id, methods=["GET"], response_model=UserResponse
        )
        self.router.add_api_route(
            "",
            self.create,
            methods=["POST"],
            response_model=UserResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            self._id_path, self.update, methods=["PUT"], response_model=UserResponse
        )
        self.router.add_api_route(
            self._id_path,
            self.delete,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @classmethod
    async def current_user(cls, request: Request) -> UserResponse:
        user_dto = request.state.user
        if not user_dto:
            raise InvalidCredentialsException()
        return UserResponse(**user_dto.__dict__)
