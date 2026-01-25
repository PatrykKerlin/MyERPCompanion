from controllers.base.base_view_controller import BaseViewController
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.theme_schema import ThemePlainSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateSchema
from services.core import GroupService, LanguageService, ThemeService, UserService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.user_view import UserView
from events.events import ViewRequested


class UserController(BaseViewController[UserService, UserView, UserPlainSchema, UserStrictUpdateSchema]):
    _plain_schema_cls = UserPlainSchema
    _strict_schema_cls = UserStrictUpdateSchema
    _service_cls = UserService
    _view_cls = UserView
    _endpoint = Endpoint.USERS
    _view_key = View.USERS

    def __init__(self, context):
        super().__init__(context)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__theme_service = ThemeService(self._settings, self._logger, self._tokens_accessor)
        self.__group_service = GroupService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UserView:
        languages = await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, self._module_id)
        themes = await self.__theme_service.get_all(Endpoint.THEMES, None, None, None, self._module_id)
        groups = await self.__group_service.get_all(Endpoint.GROUPS, None, None, None, self._module_id)
        language_pairs = [(language.id, language.key) for language in languages]
        theme_pairs = [(theme.id, theme.key) for theme in themes]
        group_pairs = [(group.id, group.key) for group in groups]
        return UserView(self, translation, mode, event.view_key, event.data, language_pairs, theme_pairs, group_pairs)

    def set_field_value(self, key: str, value):
        if key == "groups":
            if value is None:
                parsed = []
            else:
                raw = str(value)
                parsed = [int(part) for part in raw.split(",") if part.strip().isdigit()]
            super().set_field_value(key, parsed)
            return
        super().set_field_value(key, value)
