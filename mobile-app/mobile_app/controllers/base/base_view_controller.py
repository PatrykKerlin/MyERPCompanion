from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from datetime import date, datetime
from typing import Any, Callable, Generic, TypeVar

from config.context import Context
from controllers.base.base_controller import BaseController
from events.events import LogoutRequested, ViewReady, ViewRequested
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import ApiActionError, Endpoint, View
from utils.media_url import MediaUrl
from utils.translation import Translation
from views.base.base_view import BaseView

TService = TypeVar("TService", bound=BaseService)
TView = TypeVar("TView", bound=BaseView)
TControllerPlainSchema = TypeVar("TControllerPlainSchema", bound=BasePlainSchema)
TControllerStrictSchema = TypeVar("TControllerStrictSchema", bound=BaseStrictSchema)
TServicePlainSchema = TypeVar("TServicePlainSchema", bound=BasePlainSchema)
TServiceStrictSchema = TypeVar("TServiceStrictSchema", bound=BaseStrictSchema)


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
        self._caller_view_key: View | None = None
        self._caller_data: dict[str, Any] | None = None
        self._subscribe_event_handlers(
            {
                ViewRequested: self.__view_requested_handler,
                LogoutRequested: self.__logout_requested_handler,
            }
        )

    @property
    def caller_view_key(self) -> View | None:
        return self._caller_view_key

    @property
    def caller_data(self) -> dict[str, Any] | None:
        return self._caller_data

    def on_value_changed(self, key: str, *after_change: Callable[[], None]) -> None:
        if self._view:
            self._view.set_field_error(key, None)
        for callback in after_change:
            callback()

    @abstractmethod
    async def _build_view(self, translation: Translation, event: ViewRequested) -> TView: ...

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_one(
        self,
        id: int,
        service: BaseService[TServicePlainSchema, TServiceStrictSchema],
        endpoint: Endpoint,
    ) -> TServicePlainSchema:
        return await service.get_one(endpoint, id, None, None, self._module_id)

    def _normalize_data(self, data: dict[str, Any]) -> None:
        if not data:
            return
        api_url = self._settings.PUBLIC_API_URL or self._settings.API_URL
        images = data.get("images")
        if isinstance(images, list):
            for image in images:
                if isinstance(image, dict):
                    url = image.get("url")
                    if isinstance(url, str):
                        image["url"] = MediaUrl.normalize(url, api_url)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                data[key] = value.isoformat()

    async def __view_requested_handler(self, event: ViewRequested) -> None:
        if event.view_key != self._view_key:
            return
        await self._open_loading_dialog()
        try:
            translation = self._state_store.app_state.translation.items
            self._module_id = event.module_id

            data = event.data
            if data is None and event.record_id is not None:
                response = await self._perform_get_one(event.record_id, self._service, self._endpoint)
                if response is not None:
                    data = response.model_dump()

            if data is not None:
                self._normalize_data(data)

            self._caller_view_key = event.caller_view_key
            self._caller_data = event.caller_data if isinstance(event.caller_data, dict) else None

            self._view = await self._build_view(translation, replace(event, data=data))
            await self._event_bus.publish(
                ViewReady(
                    view_key=event.view_key,
                    record_id=event.record_id,
                    view=self._view,
                )
            )
        finally:
            self._close_loading_dialog()

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        self._view = None
