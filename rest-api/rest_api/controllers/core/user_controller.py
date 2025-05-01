from typing import Annotated, Union

from fastapi import Body, Request, status

from config import Context
from controllers.base import BaseController
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.core import SettingService, UserService
from utils.auth import Auth
from utils.exceptions import InvalidCredentialsException
from utils.validators import SettingsValidator


class UserController(
    BaseController[
        UserService,
        Union[UserInputCreateSchema, UserInputUpdateSchema],
        UserOutputSchema,
    ]
):
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.setting_service = SettingService()
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserOutputSchema,
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(UserOutputSchema)

    @Auth.restrict_access()
    async def create(
        self, request: Request, data: Annotated[UserInputCreateSchema | UserInputUpdateSchema, Body()]
    ) -> UserOutputSchema:
        await self.__validate_settings(data)
        return await super().create(request=request, data=data)

    @Auth.restrict_access()
    async def update(
        self, request: Request, data: Annotated[UserInputCreateSchema | UserInputUpdateSchema, Body()], model_id: int
    ) -> UserOutputSchema:
        await self.__validate_settings(data)
        return await super().update(request=request, data=data, model_id=model_id)

    @Auth.restrict_access()
    async def current_user(self, request: Request) -> UserOutputSchema:
        user = request.state.user
        if not user:
            raise InvalidCredentialsException()
        return UserOutputSchema.model_construct(**user.model_dump())

    async def __validate_settings(self, data: UserInputCreateSchema | UserInputUpdateSchema) -> None:
        async with self._get_session() as session:
            await SettingsValidator.validate_key(session, self.setting_service, data.language_id, "language")
            await SettingsValidator.validate_key(session, self.setting_service, data.theme_id, "theme")
