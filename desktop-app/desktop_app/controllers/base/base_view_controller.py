from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar, cast

import flet as ft
from httpx import HTTPStatusError
from pydantic import ValidationError

from controllers.base.base_controller import BaseController
from events.events import (
    DialogReady,
    DialogRequested,
    RecordDeleteRequested,
    TabClosed,
    TabCloseRequested,
    TabRequested,
    ViewReady,
    ViewRequested,
)
from schemas.base import BaseStrictSchema, BasePlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.base.base_service import BaseService
from states.states import ViewState
from utils.enums import Endpoint, View, ViewMode
from utils.request_data import RequestData
from utils.translation import Translation
from views.base.base_view import BaseView
from config.context import Context
from views.components.view_dialog_component import ViewDialog

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
    _view_key: View

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._module_id = 0
        self._service = self._service_cls(self._settings, self._logger, self._tokens_accessor)
        self._view: TView | None = None
        self._request_data = RequestData()
        self._page_size_list = [5, 10, 25, 50, 100]
        self.__prev_mode: ViewMode | None = None
        self._subscribe_event_handlers(
            {
                TabClosed: self.__tab_closed_handler,
                RecordDeleteRequested: self.__record_delete_requested_handler,
                ViewRequested: self.__view_requested_handler,
                DialogRequested: self.__dialog_requested_handler,
                DialogReady: self.__dialog_ready_handler,
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

    @abstractmethod
    async def _build_view(
        self, translation: Translation, mode: ViewMode, event: ViewRequested | DialogRequested
    ) -> TView: ...

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
        self._page.run_task(self._execute_row_clicked, result_id)

    def on_back_clicked(self) -> None:
        if not self._view:
            return
        self._view.toggle_search_results()
        self._state_store.update(view={"mode": ViewMode.SEARCH})

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__execute_save_clicked)

    def on_cancel_clicked(self) -> None:
        if not self._view:
            return
        if self._view.mode == ViewMode.CREATE:
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

    def set_field_value(self, key: str, value: str | int | float | bool | None) -> None:
        if not self._view:
            return
        parsed_value = self.__parse_value(value)
        self._request_data.input_values[key] = parsed_value
        error = self.__validate_field(key)
        self._view.set_field_error(key, error)

    def get_search_result_columns(self, available_fields: list[str]) -> list[str]:
        return available_fields

    async def _perform_get_page(self, endpoint: Endpoint | None = None) -> PaginatedResponseSchema[TPlainSchema]:
        if not endpoint:
            endpoint = self._endpoint
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
            endpoint=endpoint,
            query_params=params,
            module_id=self._module_id,
        )

    async def _perform_get_one(
        self, id: int, service: BaseService | None = None, endpoint: Endpoint | None = None
    ) -> TPlainSchema:
        if not endpoint:
            endpoint = self._endpoint
        if not service:
            service = self._service
        return await service.call_api_with_token_refresh(
            func=service.get_one,
            endpoint=endpoint,
            path_param=id,
            module_id=self._module_id,
        )

    async def _perform_create(self, endpoint: Endpoint | None = None) -> TPlainSchema:
        if not endpoint:
            endpoint = self._endpoint
        data = self._strict_schema_cls(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.create,
            endpoint=endpoint,
            body_params=data,
            module_id=self._module_id,
        )

    async def _perform_update(self, id: int, endpoint: Endpoint | None = None) -> TPlainSchema:
        if not endpoint:
            endpoint = self._endpoint
        data = self._strict_schema_cls(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.update,
            endpoint=endpoint,
            path_param=id,
            body_params=data,
            module_id=self._module_id,
        )

    async def _perform_delete(self, id: int, endpoint: Endpoint | None = None) -> bool:
        if not endpoint:
            endpoint = self._endpoint
        return await self._service.call_api_with_token_refresh(
            func=self._service.delete,
            endpoint=endpoint,
            path_param=id,
            module_id=self._module_id,
        )

    async def _execute_row_clicked(
        self,
        result_id: int,
        view_key: View | None = None,
        service: BaseService | None = None,
        endpoint: Endpoint | None = None,
    ) -> None:
        self._open_loading_dialog()
        try:
            response = await self._perform_get_one(result_id, service, endpoint)
            if not view_key:
                view_key = self._view_key
            await self._event_bus.publish(
                TabRequested(
                    module_id=self._module_id,
                    view_key=view_key,
                    record_id=response.id,
                    record_data=response.model_dump(),
                )
            )
            self._close_loading_dialog()
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_error_dialog(message_key="data_fetch_fail")

    async def __view_requested_handler(self, event: ViewRequested) -> None:
        if event.view_key != self._view_key:
            return
        self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        self._module_id = event.module_id
        mode = ViewMode.READ if event.data else ViewMode.SEARCH
        if event.data:
            self._request_data.input_values = dict(event.data)
        self._view = await self._build_view(translation, mode, event)
        await self._event_bus.publish(ViewReady(view_key=event.view_key, record_id=event.record_id, view=self._view))
        self._close_loading_dialog()

    async def __dialog_requested_handler(self, event: DialogRequested) -> None:
        if event.view_key != self._view_key:
            return
        self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        self._module_id = event.module_id
        mode = ViewMode.CREATE
        if event.data:
            self._request_data.input_values = dict(event.data)
        self._view = await self._build_view(translation, mode, event)
        await self._event_bus.publish(DialogReady(view_key=self._view_key, view=self._view))
        self._close_loading_dialog()

    async def __dialog_ready_handler(self, event: DialogReady) -> None:
        if event.view_key != self._view_key:
            return
        translation = self._state_store.app_state.translation.items
        dialog_title = translation.get("add_new_record")
        view_dialog = ViewDialog(
            view=event.view,
            title=dialog_title,
        )
        self._page.show_dialog(view_dialog)

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        if event.view.view_key != self._view_key:
            return
        self._request_data = RequestData()

    async def __record_delete_requested_handler(self, event: RecordDeleteRequested) -> None:
        if event.view_key != self._view_key:
            return
        self._open_loading_dialog()
        try:
            await self._perform_delete(event.id)
            tab_title = self._get_tab_title(event.view_key, event.id)
            await self._event_bus.publish(TabCloseRequested(tab_title))
            self._close_loading_dialog()
            await self.__execute_search_clicked()
            self._open_message_dialog("record_delete_success")
        except HTTPStatusError as http_error:
            self._close_loading_dialog()
            if http_error.response.status_code == 403:
                self._open_error_dialog(message_key="no_permissions")
            else:
                self._logger.error(str(http_error))
                self._open_error_dialog(message_key="record_delete_fail")
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_error_dialog(message_key="record_delete_fail")

    def __view_updated_listener(self, state: ViewState) -> None:
        if not state.title:
            self._view = None
        elif isinstance(state.view, self._view_cls):
            self._view = cast(TView, state.view)
            if not self.__prev_mode or self.__prev_mode != ViewMode.LIST:
                self.__prev_mode = self._view.mode
                self._view.set_mode(state.mode)

    def __parse_value(self, value: str | int | float | bool | None) -> str | int | float | bool | None:
        if value is None:
            return None
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
                self._state_store.update(view={"mode": ViewMode.LIST})
                self._close_loading_dialog()
            else:
                self._close_loading_dialog()
                self._open_message_dialog("no_records_found")
        except Exception as err:
            self._close_loading_dialog()
            self._logger.error(str(err))
            self._open_message_dialog("no_records_found")

    async def __execute_save_clicked(self) -> None:
        if not self._view:
            return
        self._open_loading_dialog()
        try:
            response: TPlainSchema | None = None
            replace_view = False
            if self._view.mode == ViewMode.CREATE:
                response = await self._perform_create()
            elif self._view.mode == ViewMode.EDIT:
                response = await self._perform_update(self._request_data.input_values["id"])
                replace_view = True
            if response:
                await self._event_bus.publish(
                    TabRequested(
                        module_id=self._module_id,
                        view_key=self._view_key,
                        record_id=response.id,
                        record_data=response.model_dump(),
                        replace_view=replace_view,
                    )
                )
            self._close_loading_dialog()
            self._open_message_dialog("record_save_success")
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
        except HTTPStatusError as http_error:
            self._close_loading_dialog()
            if http_error.response.status_code == 403:
                self._open_error_dialog(message_key="no_permissions")
            else:
                self._logger.error(str(http_error))
                self._open_error_dialog(message_key="record_save_fail")
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
