# pyright: reportIncompatibleMethodOverride=false

from typing import Callable, List, Union

from fastapi import Request, Response, status

from config import Context
from controllers.base import BaseController
from schemas.core import UserCreate, UserResponse, UserUpdate
from services.core import UserService
from utils import AuthUtil
from utils.exceptions import InvalidCredentialsException

UserCreateOrUpdate = Union[UserCreate, UserUpdate]


class UserController(BaseController[UserService, UserCreateOrUpdate, UserResponse]):
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        path = ""
        self._register_routes(path, "/user_id", UserResponse)
        self.router.add_api_route(
            path=path + "/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserResponse,
            status_code=status.HTTP_200_OK,
        )

    @AuthUtil.restrict_access()
    async def get_all(self, request: Request) -> list[UserResponse]:
        return await super().get_all(request)

    @AuthUtil.restrict_access()
    async def get_by_id(self, request: Request, user_id: int) -> UserResponse:
        return await super().get_by_id(request, user_id)

    @AuthUtil.restrict_access()
    async def create(self, data: UserCreate, request: Request) -> UserResponse:
        return await super().create(data, request)

    @AuthUtil.restrict_access()
    async def update(
        self, data: UserUpdate, request: Request, user_id: int
    ) -> UserResponse:
        return await super().update(data, request, user_id)

    @AuthUtil.restrict_access()
    async def delete(self, request: Request, user_id: int) -> Response:
        return await super().delete(request, user_id)

    @classmethod
    async def current_user(cls, request: Request) -> UserResponse:
        user_internal = request.state.user
        if not user_internal:
            raise InvalidCredentialsException()
        return UserResponse.model_construct(**user_internal.model_dump())
