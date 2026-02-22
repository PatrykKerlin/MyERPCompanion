from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_controller import BaseController
from events.events import TranslationFailed, TranslationReady, TranslationRequested
from services.core.translation_service import TranslationService
from utils.enums import ApiActionError
from utils.translation import Translation

if TYPE_CHECKING:
    from config.context import Context


class TranslationController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = TranslationService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers({TranslationRequested: self.__translations_requested_handler})

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_fetch_translation_items(self, language: str) -> dict[str, str] | None:
        return await self.__service.fetch_translation_items(language)

    async def __translations_requested_handler(self, event: TranslationRequested) -> None:
        translation_items = await self.__perform_fetch_translation_items(event.language)
        if translation_items is None:
            await self._event_bus.publish(TranslationFailed())
            return
        translation = Translation(translation_items)
        self._state_store.update(translation={"language": event.language, "items": translation})
        await self._event_bus.publish(TranslationReady(event.user_authenticated))
