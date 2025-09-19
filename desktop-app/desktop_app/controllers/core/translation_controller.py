from __future__ import annotations

from typing import TYPE_CHECKING
from events.types import ApiReady, TranslationRequested, TranslationLoaded, TranslationFailed, TranslationReady
from services.core.translation_service import TranslationService
from states.states import TranslationState
from controllers.base.base_controller import BaseController

if TYPE_CHECKING:
    from config.context import Context


class TranslationController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._service = TranslationService(self._context.settings, self._context.logger)

        event_handlers = {
            ApiReady: self._on_api_ready,
            TranslationRequested: self._on_translations_requested,
            TranslationLoaded: self._on_translations_loaded,
            TranslationFailed: self._on_translations_failed,
        }
        for event, handler in event_handlers.items():
            unsubscriber = self._context.event_bus.subscribe(event.event_type(), handler)
            self.add_unsubscriber(unsubscriber)

    async def _on_api_ready(self, _: ApiReady) -> None:
        current_language = self._context.settings.LANGUAGE
        self._context.state_store.update(
            lambda state: state.model_copy(
                update={
                    "translation": state.translation.model_copy(update={"language": current_language, "success": False})
                }
            )
        )
        await self._context.event_bus.publish(TranslationRequested(language=current_language))

    async def _on_translations_requested(self, event: TranslationRequested) -> None:
        try:
            fetched_items = await self._service.fetch_translations(event.language)
            await self._context.event_bus.publish(TranslationLoaded(language=event.language, items=fetched_items))
        except Exception as exception:
            self._context.logger.error(str(exception))
            await self._context.event_bus.publish(TranslationFailed(language=event.language))

    async def _on_translations_loaded(self, event: TranslationLoaded) -> None:
        self._context.state_store.update(
            lambda state: state.model_copy(
                update={
                    "translation": TranslationState(
                        language=event.language, items={**state.translation.items, **event.items}, success=True
                    )
                }
            )
        )
        await self._context.event_bus.publish(TranslationReady())

    async def _on_translations_failed(self, event: TranslationFailed) -> None:
        self._context.state_store.update(
            lambda state: state.model_copy(
                update={
                    "translation": state.translation.model_copy(update={"language": event.language, "success": False})
                }
            )
        )
