from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar, cast
from datetime import date, datetime

import flet as ft
from pydantic import ValidationError

from controllers.base.base_controller import BaseController
from events.events import (
    RecordDeleteRequested,
    RecordSaved,
    TabClosed,
    TabCloseRequested,
    TabRequested,
    ViewReady,
    SaveSucceeded,
    ViewRequested,
)
from schemas.base import BaseStrictSchema, BasePlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.base.base_service import BaseService
from states.states import ViewState
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.request_data import RequestData
from utils.translation import Translation
from views.base.base_view import BaseView
from config.context import Context
from views.components.view_dialog_component import ViewDialog

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
        self._request_data = RequestData()
        self._request_data_by_view: dict[int, RequestData] = {}
        self._page_size_list = [5, 10, 25, 50, 100]
        self.__meta_fields = {"id", "created_by_username", "created_at", "modified_by_username", "modified_at"}
        self._subscribe_event_handlers(
            {
                TabClosed: self.__tab_closed_handler,
                RecordDeleteRequested: self.__record_delete_requested_handler,
                ViewRequested: self.__view_requested_handler,
                ViewReady: self.__view_ready_handler,
                RecordSaved: self.__record_saved_handler,
                SaveSucceeded: self.__save_succeeded_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "view": self.__view_updated_listener,
            }
        )

    @property
    def search_params(self) -> RequestData:
        return self._request_data

    @property
    def page_size_list(self) -> list[int]:
        return self._page_size_list

    @property
    def meta_fields(self) -> set[str]:
        return self.__meta_fields

    @abstractmethod
    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> TView: ...

    def on_marker_clicked(self, event: ft.ControlEvent, key: str) -> None:
        if not self._view:
            return
        marker_state = bool(getattr(event.control, "value", False))
        input_field = self._view.inputs[key].input.content
        if not input_field:
            return
        input_value = getattr(input_field, "value", None)
        self.set_field_value(key, input_value)
        self._view.set_input_state(input_field, marker_state)
        if marker_state:
            self._request_data.selected_inputs.add(key)
        else:
            self._request_data.selected_inputs.discard(key)

    def on_search_clicked(self) -> None:
        self._page.run_task(self.__execute_search_clicked)

    def on_row_clicked(self, result_id: int) -> None:
        self._page.run_task(self._execute_row_clicked, result_id, self._view_key, self._service, self._endpoint)

    def on_back_clicked(self) -> None:
        if not self._view:
            return
        self._view.search_results = None
        self._state_store.update(view={"mode": ViewMode.SEARCH})

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__execute_save_clicked)

    def on_cancel_clicked(self) -> None:
        if not self._view:
            return
        if self._view.is_dialog:
            self._state_store.update(view={"mode": ViewMode.READ})
        elif self._view.mode == ViewMode.CREATE:
            self._state_store.update(view={"mode": ViewMode.SEARCH})
        elif self._view.mode == ViewMode.EDIT:
            self._state_store.update(view={"mode": ViewMode.READ})
        self._view.clear_inputs()
        self._page.pop_dialog()

    def on_sort_clicked(self, key: str) -> None:
        if self._request_data.sort_by == key:
            self._request_data.order = "desc" if self._request_data.order == "asc" else "asc"
        else:
            self._request_data.sort_by = key
            self._request_data.order = "asc"
        self.on_search_clicked()

    def on_page_clicked(self, direction: str) -> None:
        if direction == "next" and self._request_data.has_next:
            self._request_data.page += 1
        elif direction == "prev" and self._request_data.page > 1:
            self._request_data.page -= 1
        self.on_search_clicked()

    def on_page_size_selected(self, new_size: int) -> None:
        self._request_data.page_size = new_size
        self._request_data.page = 1
        self.on_search_clicked()

    def on_value_changed(self, event: ft.ControlEvent, key: str, *after_change: Callable[[], None]) -> None:
        if hasattr(event.control, "value"):
            value = getattr(event.control, "value", None)
            self.set_field_value(key, value)
        for callback in after_change:
            callback()

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        if not self._view:
            return
        parsed_value = self.__parse_value(value)
        self._request_data.input_values[key] = parsed_value
        error = self.__validate_field(key)
        self._view.set_field_error(key, error)

    def get_search_result_columns(self, available_fields: list[str]) -> list[str]:
        return available_fields

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_page(
        self, service: BaseService[TServicePlainSchema, TServiceStrictSchema], endpoint: Endpoint
    ) -> PaginatedResponseSchema[TServicePlainSchema]:
        filters: dict[str, str] = {}
        for field in self._request_data.selected_inputs:
            filters[field] = self._request_data.input_values.get(field, "")
        params = {
            "page": self._request_data.page,
            "page_size": self._request_data.page_size,
            "sort_by": self._request_data.sort_by,
            "order": self._request_data.order,
            **filters,
        }
        return await service.get_page(endpoint, None, params, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_one(
        self, id: int, service: BaseService[TServicePlainSchema, TServiceStrictSchema], endpoint: Endpoint
    ) -> TServicePlainSchema:
        return await service.get_one(endpoint, id, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_create(
        self,
        service: BaseService[TServicePlainSchema, TServiceStrictSchema],
        endpoint: Endpoint,
        payload: TServiceStrictSchema,
    ) -> TServicePlainSchema:
        return await service.create(endpoint, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_create_bulk(
        self,
        service: BaseService[TServicePlainSchema, TServiceStrictSchema],
        endpoint: Endpoint,
        payload: list[TServiceStrictSchema],
    ) -> list[TServicePlainSchema]:
        return await service.create_bulk(endpoint, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_update(
        self,
        id: int,
        service: BaseService[TServicePlainSchema, TServiceStrictSchema],
        endpoint: Endpoint,
        payload: TServiceStrictSchema,
    ) -> TServicePlainSchema:
        return await service.update(endpoint, id, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def _perform_delete(
        self, id: int, service: BaseService[TServicePlainSchema, TServiceStrictSchema], endpoint: Endpoint
    ) -> bool:
        return await service.delete(endpoint, id, None, None, self._module_id)

    async def _execute_row_clicked(
        self,
        result_id: int,
        view_key: View,
        service: BaseService[TServicePlainSchema, TServiceStrictSchema],
        endpoint: Endpoint,
    ) -> None:
        response = await self._perform_get_one(result_id, service, endpoint)
        data = response.model_dump()
        self.__parse_data_row(data)
        await self._event_bus.publish(
            TabRequested(
                module_id=self._module_id,
                view_key=view_key,
                record_id=response.id,
                record_data=data,
            )
        )

    async def __view_requested_handler(self, event: ViewRequested) -> None:
        if event.view_key != self._view_key:
            return
        self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        self._module_id = event.module_id
        if event.is_dialog:
            mode = ViewMode.CREATE
        elif event.data:
            mode = ViewMode.READ
        else:
            mode = ViewMode.SEARCH
        self._request_data = RequestData()
        if event.data:
            self._request_data.input_values = dict(event.data)
        self._view = await self._build_view(translation, mode, event)
        if self._view:
            self._request_data_by_view[id(self._view)] = self._request_data
        await self._event_bus.publish(
            ViewReady(
                view_key=event.view_key,
                record_id=event.record_id,
                view=self._view,
                is_dialog=event.is_dialog,
                save_succeeded=event.save_succeeded,
            )
        )
        self._close_loading_dialog()

    async def __view_ready_handler(self, event: ViewReady) -> None:
        if not self._view:
            return
        if not event.is_dialog or event.view_key != self._view_key:
            return
        translation = self._state_store.app_state.translation.items
        dialog_title = translation.get("add_new_record")
        card_content = event.view.content
        dialog_view = ft.Container(content=card_content, expand=True)
        view_dialog = ViewDialog(
            view=dialog_view,
            title=dialog_title,
            width_ratio=event.width_ratio,
            actions=[self._view.buttons_row],
        )
        self._page.show_dialog(view_dialog)

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        if event.view.view_key != self._view_key:
            return
        self._request_data_by_view.pop(id(event.view), None)
        if self._view is event.view:
            self._view = None
            self._request_data = RequestData()

    async def __record_delete_requested_handler(self, event: RecordDeleteRequested) -> None:
        if event.view_key != self._view_key:
            return
        await self._perform_delete(event.id, self._service, self._endpoint)
        tab_title = self._get_tab_title(event.view_key, event.id)
        await self._event_bus.publish(TabCloseRequested(tab_title))
        await self.__execute_search_clicked()
        self._open_message_dialog("record_delete_success")

    async def __record_saved_handler(self, event: RecordSaved):
        if event.view_key != self._view_key:
            return
        if not self._view or not self._view.data_row:
            return
        response = await self._perform_get_one(self._view.data_row["id"], self._service, self._endpoint)
        await self._event_bus.publish(
            TabRequested(
                module_id=self._module_id,
                view_key=self._view_key,
                record_id=response.id,
                record_data=response.model_dump(),
                save_succeeded=True,
            )
        )

    async def __save_succeeded_handler(self, event: SaveSucceeded):
        if event.view_key != self._view_key:
            return
        self._open_message_dialog("record_save_success")

    def __view_updated_listener(self, state: ViewState) -> None:
        if not state.title:
            self._view = None
        elif isinstance(state.view, self._view_cls) and state.view.view_key == self._view_key:
            self._view = cast(TView, state.view)
            request_data = self._request_data_by_view.get(id(self._view))
            if request_data is None:
                request_data = RequestData()
                self._request_data_by_view[id(self._view)] = request_data
            self._request_data = request_data
            if self._view.mode != state.mode:
                self._view.set_mode(state.mode)

    def __parse_value(
        self, value: str | int | float | bool | date | datetime | None
    ) -> str | int | float | bool | date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, (bool, int, float)):
            return value
        value_stripped = str(value).strip()
        if value_stripped == "":
            return None
        value_lower = value_stripped.lower()
        if value_lower in {"true", "false"}:
            return value_lower == "true"
        return value_stripped

    async def __execute_search_clicked(self) -> None:
        if not self._view:
            return
        response = await self._perform_get_page(self._service, self._endpoint)
        self._request_data.total = response.total
        self._request_data.page = response.page
        self._request_data.page_size = response.page_size
        self._request_data.has_next = response.has_next
        self._request_data.has_prev = response.has_prev
        results = [result.model_dump() for result in response.items]
        if results:
            for row in results:
                self.__parse_data_row(row, True)
            self._view.search_results = results
            self._state_store.update(view={"mode": ViewMode.LIST})
        else:
            self._open_message_dialog("no_records_found")

    async def __execute_save_clicked(self) -> None:
        if not self._view:
            return
        try:
            response: TControllerPlainSchema | None = None
            if self._view.mode == ViewMode.CREATE:
                payload = self._strict_schema_cls(**self._request_data.input_values)
                response = await self._perform_create(self._service, self._endpoint, payload)
                self._view.clear_inputs()
                self._state_store.update(view={"mode": ViewMode.SEARCH})
            elif self._view.mode == ViewMode.EDIT:
                payload = self._strict_schema_cls(**self._request_data.input_values)
                response = await self._perform_update(
                    self._request_data.input_values["id"], self._service, self._endpoint, payload
                )
            if response:
                if not self._view.is_dialog:
                    await self._event_bus.publish(
                        TabRequested(
                            module_id=self._module_id,
                            view_key=self._view_key,
                            record_id=response.id,
                            record_data=response.model_dump(),
                            save_succeeded=True,
                        )
                    )
                self._request_data = RequestData()
                if self._view:
                    self._request_data_by_view[id(self._view)] = self._request_data
                if self._view and self._view.mode == ViewMode.SEARCH:
                    self._view.clear_inputs()
                if self._view.caller_view_key:
                    await self._event_bus.publish(
                        RecordSaved(
                            view_key=self._view.caller_view_key,
                        )
                    )
        except ValidationError as validation_error:
            translate_state = self._state_store.app_state.translation
            error_message = [translate_state.items.get("validation_errors")]
            for error in validation_error.errors():
                message = error.get("msg", "")
                loc = error.get("loc", ())
                if loc:
                    key = loc[0]
                    error_message.append(f"{translate_state.items.get(str(key))}: {message}")
                else:
                    error_message.append(message)
            final_message = "\n".join(error_message)
            self._open_error_dialog(message=final_message)

    def __validate_field(self, key: str) -> str | None:
        if not self._view or self._view.mode not in {ViewMode.CREATE, ViewMode.EDIT}:
            return
        field = self._view.inputs.get(key)
        if field:
            input_control = field.input.content
            if hasattr(input_control, "disabled") and getattr(input_control, "disabled"):
                return None
        self._view.set_save_button_state(True)
        if self._view.mode == ViewMode.CREATE:
            self._request_data.input_values["id"] = 1
        try:
            self._strict_schema_cls(**self._request_data.input_values)
        except ValidationError as validation_error:
            for error in validation_error.errors():
                if error["loc"] == (key,):
                    return error["msg"]
        return

    def __parse_data_row(self, data_row: dict[str, Any], parse_none: bool = False) -> None:
        for key, value in data_row.items():
            if key in self.__meta_fields and key.endswith("_at") and value is not None:
                data_row[key] = self._format_datetime(value)
            if value is None and parse_none:
                data_row[key] = ""

    def _format_datetime(self, value: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return value.strftime(fmt)
