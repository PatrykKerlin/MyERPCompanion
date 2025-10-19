from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar, cast

import flet as ft
from pydantic import ValidationError

from controllers.base.base_controller import BaseController
from events.events import RecordDeleteRequested, TabClosed, TabRequested, TabCloseRequested, ViewRequested
from schemas.base import BaseStrictSchema, BasePlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.base.base_service import BaseService
from states.states import TabsState
from utils.enums import Endpoint, ViewMode
from utils.request_data import RequestData
from views.base.base_view import BaseView
from config.context import Context

TService = TypeVar("TService", bound=BaseService)
TView = TypeVar("TView", bound=BaseView)
TPlainSchema = TypeVar("TPlainSchema", bound=BasePlainSchema)
TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)


class BaseViewController(BaseController, Generic[TService, TView, TPlainSchema, TStrictSchema], ABC):
    _plain_schema_cls: type[TPlainSchema]
    _strict_schema_cls: type[TStrictSchema]
    _service_cls: type[TService]
    _view_cls: type[TView]
    _endpoint: Endpoint

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._key = ""
        self._service = self._service_cls(self._settings, self._logger, self._tokens_accessor)
        self._view: TView | None = None
        self._request_data = RequestData()
        self._page_size_list = [5, 10, 25, 50, 100]
        self._subscribe_event_handlers(
            {
                TabClosed: self.__tab_closed_handler,
                RecordDeleteRequested: self.__record_delete_requested_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "tabs": self.__tabs_updated_listener,
            }
        )

    @property
    def search_params(self) -> RequestData:
        return self._request_data

    @property
    def page_size_list(self) -> list[int]:
        return self._page_size_list

    @abstractmethod
    async def _view_requested_handler(self, event: ViewRequested) -> None:
        pass

    async def _perform_get_page(self) -> PaginatedResponseSchema[TPlainSchema]:
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
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_page,
            endpoint=self._endpoint,
            query_params=params,
            view_key=self._key,
        )

    async def _perform_get_one(self, id: int) -> TPlainSchema:
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_one,
            endpoint=self._endpoint,
            path_param=id,
            view_key=self._key,
        )

    async def _perform_create(self) -> TPlainSchema:
        data = self._strict_schema_cls(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.create,
            endpoint=self._endpoint,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_update(self, id: int) -> TPlainSchema:
        data = self._strict_schema_cls(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.update,
            endpoint=self._endpoint,
            path_param=id,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_delete(self, id: int) -> bool:
        return await self._service.call_api_with_token_refresh(
            func=self._service.delete,
            endpoint=self._endpoint,
            path_param=id,
            view_key=self._key,
        )

    def on_marker_clicked(self, event: ft.ControlEvent, key: str) -> None:
        if not self._view:
            return
        marker_state = event.control.value
        field = self._view.inputs[key]
        input = field.input.content
        if input:
            value_parsed: str | None = None
            if hasattr(event.control, "value"):
                value = getattr(event.control, "value", None)
                value_parsed = str(value) if value is not None else None
            self.set_field_value(key, value_parsed)
            self._view.set_input_state(input, marker_state)
        if marker_state:
            self._request_data.selected_inputs.add(key)
        else:
            self._request_data.selected_inputs.discard(key)

    def on_value_changed(self, event: ft.ControlEvent, key: str, *after_change: Callable[[], None]) -> None:
        if not self._view:
            return
        if hasattr(event.control, "value"):
            value = getattr(event.control, "value", None)
            self.set_field_value(key, value)
        for callback in after_change:
            callback()

    def on_search_clicked(self) -> None:
        self._page.run_task(self.__execute_search_clicked)

    def on_row_clicked(self, result_id: int) -> None:
        self._page.run_task(self.__execute_row_clicked, result_id)

    def on_back_clicked(self) -> None:
        if not self._view:
            return
        self._view.toggle_search_results()
        tabs_state = self._state_store.app_state.tabs
        self._state_store.update(tabs={"mode": tabs_state.items[tabs_state.current].mode})

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__execute_save_clicked)

    def on_cancel_clicked(self) -> None:
        if not self._view:
            return
        if self._view.mode == ViewMode.CREATE:
            self._state_store.update(tabs={"mode": ViewMode.SEARCH})
        elif self._view.mode == ViewMode.EDIT:
            self._state_store.update(tabs={"mode": ViewMode.READ})

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

    def set_field_value(self, key: str, value: str | int | float | bool | None) -> None:
        if not self._view:
            return
        parsed_value = self.__parse_value(value)
        self._request_data.input_values[key] = parsed_value
        error = self.__validate_field(key)
        self._view.set_field_error(key, error)

    def __parse_value(self, value: str | int | float | bool | None) -> str | int | float | bool | None:
        if value is None:
            return None
        if isinstance(value, (bool, int, float)):
            return value
        value_stripped = value.strip()
        if value_stripped == "":
            return None
        lower = value_stripped.lower()
        if lower in {"true", "false"}:
            return lower == "true"
        if value_stripped.isdecimal() or (value_stripped.startswith("-") and value_stripped[1:].isdecimal()):
            return int(value_stripped)
        try:
            return float(value_stripped)
        except ValueError:
            return value_stripped

    def __tabs_updated_listener(self, state: TabsState) -> None:
        if not state.current or state.current not in state.items:
            return
        if isinstance(state.items[state.current], self._view_cls):
            self._view = cast(TView, state.items[state.current])

    async def __execute_search_clicked(self) -> None:
        if not self._view:
            return
        self._open_loading_dialog()
        try:
            response = await self._perform_get_page()
            self._request_data.total = response.total
            self._request_data.page = response.page
            self._request_data.page_size = response.page_size
            self._request_data.has_next = response.has_next
            self._request_data.has_prev = response.has_prev
            results = [result.model_dump() for result in response.items]
            if results:
                self._view.toggle_search_results(results)
                tabs_state = self._state_store.app_state.tabs
                self._state_store.update(tabs={"mode": tabs_state.items[tabs_state.current].mode})
                self._close_loading_dialog()
            else:
                self._close_loading_dialog()
                self._open_message_dialog("no_records_found")
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_message_dialog("no_records_found")

    async def __execute_row_clicked(self, result_id: int) -> None:
        self._open_loading_dialog()
        try:
            response = await self._perform_get_one(result_id)
            await self._event_bus.publish(TabRequested(key=self._key, postfix=response.id, data=response.model_dump()))
            self._close_loading_dialog()
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_error_dialog(message_key="data_fetch_fail")

    async def __execute_save_clicked(self) -> None:
        if not self._view:
            return
        self._open_loading_dialog()
        try:
            response: TPlainSchema | None = None
            replace = False
            if self._view.mode == ViewMode.CREATE:
                response = await self._perform_create()
            elif self._view.mode == ViewMode.EDIT:
                print(self._request_data.input_values)
                response = await self._perform_update(self._request_data.input_values["id"])
                replace = True
            self._close_loading_dialog()
            self._open_message_dialog("record_save_success")
            if not response:
                return
            await self._event_bus.publish(
                TabRequested(key=self._key, postfix=response.id, data=response.model_dump(), replace=replace)
            )

        except ValidationError as validation_error:
            translate_state = self._state_store.app_state.translation
            error_message = [translate_state.items.get("validation_errors")]
            for error in validation_error.errors():
                key = error["loc"][0]
                message = error["msg"]
                error_message.append(f"{translate_state.items.get(str(key))}: {message}")
            final_message = "\n".join(error_message)
            self._close_loading_dialog()
            self._open_error_dialog(message=final_message)
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_error_dialog(message_key="record_save_fail")

    def __validate_field(self, key: str) -> str | None:
        if not self._view or self._view.mode not in {ViewMode.CREATE, ViewMode.EDIT}:
            return
        if self._view.mode == ViewMode.CREATE:
            self._request_data.input_values["id"] = 1
        try:
            self._strict_schema_cls(**self._request_data.input_values)
            self._view.set_save_button_state(True)
        except ValidationError as validation_error:
            self._view.set_save_button_state(False)
            for error in validation_error.errors():
                if error["loc"] == (key,):
                    return error["msg"]
        return

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        if event.key != self._key:
            return
        self._request_data = RequestData()

    async def __record_delete_requested_handler(self, event: RecordDeleteRequested) -> None:
        if event.key != self._key:
            return
        self._open_loading_dialog()
        try:
            await self._perform_delete(event.id)
            tab_title = self._get_tab_title(event.key, event.id)
            await self._event_bus.publish(TabCloseRequested(tab_title))
            self._open_message_dialog("record_delete_success")
            self._close_loading_dialog()
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_error_dialog(message_key="record_delete_fail")

    # def get_constraint(self, field: str, constraint: str) -> Any:
    #     metadata = self._output_schema_cls.model_fields[field].metadata
    #     for item in metadata:
    #         if hasattr(item, constraint):
    #             return getattr(item, constraint)
    #     return None

    # def toggle_search_marker(
    #     self, event: ft.ControlEvent, key: str, inputs: dict[str, ft.TextField | ft.Dropdown | ft.Checkbox]
    # ) -> None:
    #     if not self._view:
    #         return
    #     enabled = event.control.value
    #     self._view.set_input_enabled(key, enabled, inputs)
    #     if enabled:
    #         self._filters.add(key)
    #         self._input_values[key] = inputs[key].value or ""
    #         error = self.__validate_field(key)
    #         if self._view:
    #             self._view.set_field_error(key, error)
    #     else:
    #         self._filters.discard(key)
    #         if self._view:
    #             self._view.set_field_error(key, None)

    # def reset_view(self) -> None:
    #     self._input_values.clear()
    #     self._filters.clear()
    #     if self._view:
    #         self._view.set_search_mode()
    #         self._view.clear_inputs()
    #         self._view.clear_search_markers()
