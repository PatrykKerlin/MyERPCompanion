from __future__ import annotations

from typing import TYPE_CHECKING
from events.events import TranslationRequested, TranslationReady, TranslationFailed
from services.core.translation_service import TranslationService
from controllers.base.base_controller import BaseController
from utils.translation import Translation

if TYPE_CHECKING:
    from config.context import Context


class TranslationController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._service = TranslationService(self._settings, self._logger, self._tokens_accessor)

        self._subscribe_event_handlers({TranslationRequested: self.__translations_requested_handler})

    async def __translations_requested_handler(self, event: TranslationRequested) -> None:
        try:
            translation_items = await self._service.fetch_translation_items(event.language)
            translation = Translation(translation_items)
            self._state_store.update(translation={"language": event.language, "items": translation})
            await self._event_bus.publish(TranslationReady(event.user_authenticated))
        except Exception:
            self._logger.exception(f"Unhandled exception in {self.__translations_requested_handler.__qualname__}")
            await self._event_bus.publish(TranslationFailed())
