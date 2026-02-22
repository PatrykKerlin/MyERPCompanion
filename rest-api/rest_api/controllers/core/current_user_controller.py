from typing import Union

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import HTTPException, Request, status
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateApiSchema, UserStrictUpdateApiSchema
from services.core import UserService
from utils.auth import Auth
from utils.enums import Permission


class CurrentUserController(
    BaseController[UserService, Union[UserStrictCreateApiSchema, UserStrictUpdateApiSchema], UserPlainSchema]
):
    _input_schema_cls = UserStrictCreateApiSchema
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

    @BaseController.handle_exceptions()
    async def current_user(self, request: Request) -> UserPlainSchema:
        user = getattr(request.state, "user", None)
        if user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return user
