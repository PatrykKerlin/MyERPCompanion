from typing import Union

from config import Context
from controllers.base import BaseController
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.core import SettingService, UserService
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
        self.__setting_service = SettingService()
        self._register_routes(UserOutputSchema)

    async def _validate_data(self, data: UserInputCreateSchema | UserInputUpdateSchema) -> None:
        async with self._get_session() as session:
            await SettingsValidator.validate_key(session, self.__setting_service, data.language_id, "language")
            await SettingsValidator.validate_key(session, self.__setting_service, data.theme_id, "theme")
