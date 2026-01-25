from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_view_controller import BaseViewController
from events.events import TranslationRequested, TranslationReady, TranslationFailed, ViewRequested
from schemas.core.translation_schema import TranslationPlainSchema, TranslationStrictSchema
from services.core import LanguageService, TranslationService
from utils.enums import Endpoint, View, ViewMode
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
        languages = await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, self._module_id)
        language_pairs = [(language.id, language.key) for language in languages]
        return TranslationView(self, translation, mode, event.view_key, event.data, language_pairs)

    async def __translations_requested_handler(self, event: TranslationRequested) -> None:
        try:
            translation_items = await self._service.fetch_translation_items(event.language)
            translation = Translation(translation_items)
            self._state_store.update(translation={"language": event.language, "items": translation})
            await self._event_bus.publish(TranslationReady(event.user_authenticated))
        except Exception:
            self._logger.exception(f"Unhandled exception in {self.__translations_requested_handler.__qualname__}")
            await self._event_bus.publish(TranslationFailed())
