from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateSchema
from services.core import GroupService, LanguageService, UserService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
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
        self.__group_service = GroupService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UserView:
        languages = await self.__perform_get_all_languages()
        language_pairs = [(language.id, language.key) for language in languages]
        theme_pairs = [
            ("system", translation.get("system")),
            ("dark", translation.get("dark")),
            ("light", translation.get("light")),
        ]
        return UserView(self, translation, mode, event.view_key, event.data, language_pairs, theme_pairs)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema]:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, self._module_id)
