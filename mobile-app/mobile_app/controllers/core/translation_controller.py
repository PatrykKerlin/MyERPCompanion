from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import TranslationFailed, TranslationReady, TranslationRequested, ViewRequested
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.translation_schema import TranslationPlainSchema, TranslationStrictSchema
from services.core import LanguageService, TranslationService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.translation_view import TranslationView

if TYPE_CHECKING:
    from config.context import Context


class TranslationController(
    BaseViewController[TranslationService, TranslationView, TranslationPlainSchema, TranslationStrictSchema]
):
    _plain_schema_cls = TranslationPlainSchema
    _strict_schema_cls = TranslationStrictSchema
    _service_cls = TranslationService
    _view_cls = TranslationView
    _endpoint = Endpoint.TRANSLATIONS
    _view_key = View.TRANSLATIONS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers({TranslationRequested: self.__translations_requested_handler})

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> TranslationView:
        languages = await self.__perform_get_all_languages()
        language_pairs = [(language.id, language.key) for language in languages]
        return TranslationView(self, translation, mode, event.view_key, event.data, language_pairs)

    async def __translations_requested_handler(self, event: TranslationRequested) -> None:
        translation_items = await self.__perform_fetch_translation_items(event.language)
        if translation_items is None:
            await self._event_bus.publish(TranslationFailed())
            return
        translation = Translation(translation_items)
        self._state_store.update(translation={"language": event.language, "items": translation})
        await self._event_bus.publish(TranslationReady(event.user_authenticated))

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema]:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_fetch_translation_items(self, language: str) -> dict[str, str] | None:
        return await self._service.fetch_translation_items(language)
