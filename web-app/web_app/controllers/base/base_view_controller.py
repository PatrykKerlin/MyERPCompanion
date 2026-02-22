from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from config.context import Context
from controllers.base.base_controller import BaseController
from events.events import ViewRequested
from schemas.base import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint, View
from utils.translation import Translation
from views.base.base_view import BaseView

TService = TypeVar("TService", bound=BaseService)
TView = TypeVar("TView", bound=BaseView)
TControllerPlainSchema = TypeVar("TControllerPlainSchema", bound=BasePlainSchema)
TControllerStrictSchema = TypeVar("TControllerStrictSchema", bound=BaseStrictSchema)


class BaseViewController(
    BaseController, Generic[TService, TView, TControllerPlainSchema, TControllerStrictSchema], ABC
):
    _plain_schema_cls: type[TControllerPlainSchema]
    _strict_schema_cls: type[TControllerStrictSchema]
    _service_cls: type[TService]
    _view_cls: type[TView]
    _endpoint: Endpoint
    _view_key: View

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._module_id = 0
        self._service = self._service_cls(self._settings, self._logger, self._tokens_accessor)
        self._view: TView | None = None
        self._subscribe_event_handlers({ViewRequested: self.__view_requested_handler})

    @abstractmethod
    async def _build_view(self, translation: Translation) -> TView: ...

    async def __view_requested_handler(self, event: ViewRequested) -> None:
        if event.view_key != self._view_key:
            return
        await self._open_loading_dialog()
        try:
            translation = self._state_store.app_state.translation.items
            self._module_id = event.module_id
            self._view = await self._build_view(translation)
            self._state_store.update(
                view={
                    "view": self._view,
                }
            )
        finally:
            self._close_loading_dialog()
