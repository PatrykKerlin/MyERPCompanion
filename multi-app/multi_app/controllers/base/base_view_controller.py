from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar, cast
from datetime import date, datetime
import json

import flet as ft
from pydantic import ValidationError

from controllers.base.base_controller import BaseController
from events.events import (
    RecordDeleteRequested,
    CallerActionRequested,
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
from utils.media_url import normalize_media_url
from views.base.base_view import BaseView
from views.components.message_dialog_component import MessageDialogComponent
from views.controls.date_field_control import DateField
from views.controls.numeric_field_control import NumericField
from config.context import Context

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
        self._request_data.page = 1
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
        if self._view.mode == ViewMode.CREATE and self._request_data.caller_view_key:
            title = self._state_store.app_state.view.title
            if title:
                self._page.run_task(self._event_bus.publish, TabCloseRequested(title))
            return
        if self._view.mode == ViewMode.CREATE:
            self._request_data.input_values.clear()
            self._request_data.selected_inputs.clear()
            self._state_store.update(view={"mode": ViewMode.SEARCH})
        elif self._view.mode == ViewMode.EDIT:
            self._state_store.update(view={"mode": ViewMode.READ})
        self._view.clear_inputs()

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
        self._page.run_task(self.__execute_search_clicked)

    def on_page_size_selected(self, new_size: int) -> None:
        self._request_data.page_size = new_size
        self._request_data.page = 1
        self.on_search_clicked()

    def on_value_changed(self, event: ft.ControlEvent, key: str, *after_change: Callable[[], None]) -> None:
        if hasattr(event.control, "value"):
            value = getattr(event.control, "value", None)
            parsed_value = self.__parse_value(value)
            self.__record_undo_state(key, parsed_value)
            self.__set_field_value_no_history(key, parsed_value)
        for callback in after_change:
            callback()

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        self.__set_field_value_no_history(key, value)

    def on_undo_clicked(self) -> None:
        if not self._view or not self._request_data.undo_stack:
            return
        key, old_value, new_value = self._request_data.undo_stack.pop()
        self._request_data.redo_stack.append((key, old_value, new_value))
        self.__apply_field_value(key, old_value)

    def on_redo_clicked(self) -> None:
        if not self._view or not self._request_data.redo_stack:
            return
        key, old_value, new_value = self._request_data.redo_stack.pop()
        self._request_data.undo_stack.append((key, old_value, new_value))
        self.__apply_field_value(key, new_value)

    def on_copy_clicked(self) -> None:
        self._page.run_task(self.__copy_inputs_to_clipboard)

    def on_paste_clicked(self) -> None:
        self._page.run_task(self.__paste_inputs_from_clipboard)

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
        self._parse_data_row(data)
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
        await self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        self._module_id = event.module_id
        data = event.data
        if (
            data is None
            and event.record_id is not None
            and (event.mode == ViewMode.READ or event.mode == ViewMode.EDIT)
        ):
            response = await self._perform_get_one(event.record_id, self._service, self._endpoint)
            data = response.model_dump()
        if data is not None:
            self._parse_data_row(data)
            if event.data is None:
                object.__setattr__(event, "data", data)
        if event.mode is not None:
            mode = event.mode
        elif data:
            mode = ViewMode.READ
        else:
            mode = ViewMode.SEARCH
        self._request_data = RequestData()
        self._request_data.caller_view_key = event.caller_view_key
        self._request_data.caller_data = event.caller_data
        if data:
            self._request_data.input_values = dict(data)
            if self._view_key == View.USERS:
                self._request_data.input_values["language_id"] = data["language"]["id"]
        self._view = await self._build_view(translation, mode, event)
        if self._view:
            self._request_data_by_view[id(self._view)] = self._request_data
        await self._event_bus.publish(
            ViewReady(
                view_key=event.view_key,
                record_id=event.record_id,
                view=self._view,
                save_succeeded=event.save_succeeded,
            )
        )
        self._close_loading_dialog()

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        if event.view.view_key != self._view_key:
            return
        if self._view is event.view:
            self._view = None
            self._request_data = RequestData()
        self._request_data_by_view.pop(id(event.view), None)

    def __open_save_success_dialog(self, close_tab_title: str | None) -> None:
        translation = self._state_store.app_state.translation.items

        def on_ok(_: ft.Event[ft.TextButton]) -> None:
            self._page.pop_dialog()
            if close_tab_title:
                self._page.run_task(self._event_bus.publish, TabCloseRequested(close_tab_title))

        message_dialog = MessageDialogComponent(
            translation=translation,
            message_key="record_save_success",
            on_ok_clicked=on_ok,
        )
        self._queue_dialog(message_dialog)

    async def __record_delete_requested_handler(self, event: RecordDeleteRequested) -> None:
        if event.view_key != self._view_key:
            return
        confirm = await self._show_confirm_dialog("confirm_delete_record")
        if not confirm:
            return
        await self._perform_delete(event.id, self._service, self._endpoint)
        tab_title = self._get_tab_title(event.view_key, event.id)
        await self._event_bus.publish(TabCloseRequested(tab_title))
        if self._view and self._view.mode in {ViewMode.SEARCH, ViewMode.LIST}:
            await self.__execute_search_clicked()
        self._open_message_dialog("record_delete_success")

    async def __save_succeeded_handler(self, event: SaveSucceeded):
        if event.view_key != self._view_key:
            return
        self.__open_save_success_dialog(None)

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

    def _parse_data_row(self, data_row: dict[str, Any], is_list: bool = False) -> None:
        if not data_row:
            return
        api_url = self._settings.API_URL
        if self._settings.CLIENT == "web" and self._settings.PUBLIC_API_URL:
            api_url = self._settings.PUBLIC_API_URL
        images = data_row.get("images")
        if isinstance(images, list):
            for image in images:
                if not isinstance(image, dict):
                    continue
                url = image.get("url")
                if isinstance(url, str):
                    image["url"] = normalize_media_url(url, api_url)
        for key, value in list(data_row.items()):
            if isinstance(value, datetime):
                data_row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                data_row[key] = value.isoformat()
            elif isinstance(value, (str, list, dict)):
                continue
        if is_list:
            return

    def _format_datetime(self, value: datetime | date | str | None) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)

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

    def __record_undo_state(self, key: str, new_value: Any) -> None:
        if not self._view:
            return
        current_value = self._request_data.input_values.get(key, self.__get_control_value(key))
        current_value = self.__parse_value(current_value)
        if current_value == new_value:
            return
        self._request_data.undo_stack.append((key, current_value, new_value))
        if len(self._request_data.undo_stack) > 100:
            self._request_data.undo_stack.pop(0)
        self._request_data.redo_stack.clear()

    def __get_control_value(self, key: str) -> Any:
        if not self._view:
            return None
        field = self._view.inputs.get(key)
        if not field:
            return None
        control = field.input.content
        if control is None:
            return None
        return getattr(control, "value", None)

    def __set_field_value_no_history(self, key: str, value: Any) -> None:
        if not self._view:
            return
        parsed_value = self.__parse_value(value)
        self._request_data.input_values[key] = parsed_value
        error = self.__validate_field(key)
        self._view.set_field_error(key, error)

    def __apply_field_value(self, key: str, value: Any) -> None:
        if not self._view:
            return
        field = self._view.inputs.get(key)
        if not field:
            return
        control = field.input.content
        if control is None:
            return
        if isinstance(control, ft.Dropdown):
            control.value = "0" if value is None else str(value)
        elif isinstance(control, ft.Checkbox):
            control.value = bool(value) if value is not None else False
        elif isinstance(control, NumericField):
            control.value = 0 if value is None else value
        elif isinstance(control, DateField):
            parsed_date: date | None
            if isinstance(value, str):
                try:
                    parsed_date = date.fromisoformat(value)
                except ValueError:
                    parsed_date = None
            elif isinstance(value, date):
                parsed_date = value
            else:
                parsed_date = None
            control.value = parsed_date
        elif hasattr(control, "value"):
            setattr(control, "value", "" if value is None else str(value))
        control.update()
        self.__set_field_value_no_history(key, value)

    async def __copy_inputs_to_clipboard(self) -> None:
        if not self._view:
            return
        data: dict[str, Any] = {}
        for key, field in self._view.inputs.items():
            control = field.input.content
            if control is None or not hasattr(control, "value"):
                continue
            value = getattr(control, "value", None)
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            data[key] = value
        payload = json.dumps(data)
        await ft.Clipboard().set(payload)

    async def __paste_inputs_from_clipboard(self) -> None:
        if not self._view:
            return
        payload = await ft.Clipboard().get()
        if not payload:
            return
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            self._open_error_dialog(message_key="invalid_clipboard_data")
            return
        if not isinstance(data, dict):
            self._open_error_dialog(message_key="invalid_clipboard_data")
            return
        for key, value in data.items():
            if key not in self._view.inputs:
                continue
            self.__apply_field_value(key, value)

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
                self._parse_data_row(row, True)
            self._view.search_results = results
            self._state_store.update(view={"mode": ViewMode.LIST})
        else:
            self._open_message_dialog("no_records_found")

    async def __execute_save_clicked(self) -> None:
        if not self._view:
            return
        if self._request_data.is_saving:
            return
        self._request_data.is_saving = True
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
                if self._request_data.caller_view_key:
                    close_title = self._state_store.app_state.view.title
                    await self._event_bus.publish(
                        CallerActionRequested(
                            caller_view_key=self._request_data.caller_view_key,
                            source_view_key=self._view_key,
                            created_id=response.id,
                            record_data=response.model_dump(),
                            caller_data=self._request_data.caller_data,
                        )
                    )
                    self.__open_save_success_dialog(close_title)
                else:
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
        finally:
            self._request_data.is_saving = False

    def __validate_field(self, key: str) -> str | None:
        if not self._view or self._view.mode not in {ViewMode.CREATE, ViewMode.EDIT}:
            return
        field = self._view.inputs.get(key)
        if field:
            input_control = field.input.content
            if hasattr(input_control, "disabled") and getattr(input_control, "disabled"):
                return None
        if self._view.mode == ViewMode.CREATE:
            self._request_data.input_values["id"] = 1
        try:
            self._strict_schema_cls(**self._request_data.input_values)
            return None
        except ValidationError as validation_error:
            for error in validation_error.errors():
                loc = error.get("loc", ())
                if loc and loc[0] == key:
                    return error.get("msg", "")
            return None
