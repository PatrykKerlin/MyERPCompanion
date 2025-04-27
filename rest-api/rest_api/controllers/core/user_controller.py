from typing import Union

from fastapi import Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import Context
from controllers.base import BaseController
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.core import SettingService, UserService
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
        self._register_routes(UserOutputSchema)
        self.router.add_api_route(
            path="/current-user",
            endpoint=self.current_user,
            methods=["GET"],
            response_model=UserOutputSchema,
            status_code=status.HTTP_200_OK,
        )

    async def _validate_data(
        self,
        session: AsyncSession,
        data: Union[UserInputCreateSchema, UserInputUpdateSchema],
    ) -> None:
        await SettingsValidator.validate_key(session, self.setting_service, data.language_id, "language")
        await SettingsValidator.validate_key(session, self.setting_service, data.theme_id, "theme")

    async def current_user(self, request: Request) -> UserOutputSchema:
        user_internal = request.state.user
        if not user_internal:
            raise InvalidCredentialsException()
        return UserOutputSchema.model_construct(**user_internal.model_dump())
