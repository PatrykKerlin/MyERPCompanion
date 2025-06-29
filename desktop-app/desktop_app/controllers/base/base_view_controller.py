from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import flet as ft
from httpx import HTTPStatusError
from pydantic import ValidationError

from controllers.base import BaseController
from schemas.base import BaseOutputSchema
from services.base import BaseViewService
from utils.view_modes import ViewMode
from views.base import BaseView

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.endpoint_schema import EndpointInputSchema

TService = TypeVar("TService", bound=BaseViewService)
TView = TypeVar("TView", bound=BaseView)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseViewController(BaseController, Generic[TService, TView, TOutputSchema], ABC):
    _output_schema_cls: type[TOutputSchema]
    _service_cls: type[TService]

    def __init__(self, context: Context, endpoint: EndpointInputSchema, postfix: str) -> None:
        super().__init__(context)
        self.has_validation_errors = True
        self._endpoint = endpoint
        self._postfix = postfix
        self._service = self._service_cls(context, endpoint.path)
        self._view: TView | None = None
        self._input_values: dict[str, Any] = {}
        self._active_view_keys: list[str] = []
        self._filters: set[str] = set()
        self._sort_by = "id"
        self._order = "asc"
        self._page = 1
        self._page_size = 10
        self._has_next = False
        self._has_prev = False
        self._total = 0
        self._page_sizes = [10, 25, 50, 100]

    @abstractmethod
    def get_new_view(self, data_row: dict[str, Any] | None = None, mode: ViewMode = ViewMode.SEARCH) -> TView:
        pass

    @property
    def sort_by(self) -> str:
        return self._sort_by

    @property
    def order(self) -> str:
        return self._order

    @property
    def page(self) -> int:
        return self._page

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def has_next(self) -> bool:
        return self._has_next

    @property
    def has_prev(self) -> bool:
        return self._has_prev

    @property
    def page_sizes(self) -> list[int]:
        return self._page_sizes

    @property
    def total(self) -> int:
        return self._total

    def on_search_click(self) -> None:
        future = self._context.page.run_task(self.__open_search_results_on_button_click)
        future.add_done_callback(lambda _: self._context.controllers.get("toolbar").refresh())

    def on_save_click(self) -> None:
        if not self._view:
            return
        future: Future[None] | None = None
        if self._view.mode == ViewMode.EDIT:
            future = self._context.page.run_task(self.__update_and_refresh_tab_on_button_click)
        elif self._view.mode == ViewMode.CREATE:
            future = self._context.page.run_task(self.__create_and_open_new_tab_on_button_click)
        if future:
            future.add_done_callback(lambda _: self._context.controllers.get("toolbar").refresh())

    def on_cancel_click(self) -> None:
        if not self._view:
            return
        if self._view.mode == ViewMode.EDIT:
            self.reset_view()
            self._view.restore_input_data()
            self._view.set_read_mode()
        elif self._view.mode == ViewMode.CREATE:
            self.reset_view()
            self._view.set_search_mode()
        self._context.controllers.get("toolbar").refresh()

    def on_row_click(self, result_id: int) -> None:
        future = self._context.page.run_task(self.__open_new_tab_on_row_click, result_id)
        future.add_done_callback(lambda _: self._context.controllers.get("toolbar").refresh())

    def on_back_click(self) -> None:
        if not self._view:
            return
        self._view.replace_content()
        self._context.controllers.get("toolbar").refresh()

    def on_sort_click(self, key: str) -> None:
        if self._sort_by == key:
            self._order = "desc" if self._order == "asc" else "asc"
        else:
            self._sort_by = key
            self._order = "asc"
        self.on_search_click()

    def on_page_change(self, direction: str) -> None:
        if direction == "next" and self._has_next:
            self._page += 1
        elif direction == "prev" and self._page > 1:
            self._page -= 1
        self.on_search_click()

    def on_page_size_change(self, new_size: int) -> None:
        self._page_size = new_size
        self._page = 1
        self.on_search_click()

    def on_record_delete(self) -> None:
        if not self._view or self._view.mode != ViewMode.READ:
            return
        future = self._context.page.run_task(self.__delete_and_close_tab_on_button_click)
        future.add_done_callback(lambda _: self._context.controllers.get("toolbar").refresh())

    def set_view(self, view: TView | None) -> None:
        self._view = view

    def get_constraint(self, field: str, constraint: str) -> Any:
        metadata = self._output_schema_cls.model_fields[field].metadata
        for item in metadata:
            if hasattr(item, constraint):
                return getattr(item, constraint)
        return None

    def toggle_search_marker(
        self, event: ft.ControlEvent, key: str, inputs: dict[str, ft.TextField | ft.Dropdown | ft.Checkbox]
    ) -> None:
        if not self._view:
            return
        enabled = event.control.value
        self._view.set_input_enabled(key, enabled, inputs)
        if enabled:
            self._filters.add(key)
            self._input_values[key] = inputs[key].value or ""
            error = self.__validate_field(key)
            if self._view:
                self._view.set_field_error(key, error)
        else:
            self._filters.discard(key)
            if self._view:
                self._view.set_field_error(key, None)

    def set_field_value(self, key: str, value: str) -> None:
        if not self._view:
            return
        self._input_values[key] = value
        if key in self._filters or self._view.mode in (ViewMode.CREATE, ViewMode.EDIT):
            error = self.__validate_field(key)
            if self._view:
                self._view.set_field_error(key, error)

    def reset_view(self) -> None:
        self._input_values.clear()
        self._filters.clear()
        if self._view:
            self._view.set_search_mode()
            self._view.clear_inputs()
            self._view.clear_search_markers()

    def __validate_field(self, key: str) -> str | None:
        if self._view and self._view.mode == ViewMode.CREATE:
            self._input_values["id"] = self._input_values.get("id", 1)
        try:
            self._output_schema_cls(**self._input_values)
            self.has_validation_errors = False
        except ValidationError as validation_error:
            self.has_validation_errors = True
            for error in validation_error.errors():
                if error["loc"] == (key,):
                    return error["msg"]
        return None

    async def __perform_get_all(self) -> list[dict[str, Any]]:
        filters: dict[str, str] = {}
        for field in self._filters:
            filters[field] = self._input_values.get(field, "").strip()
        result = await self._service.get_all(
            filters=filters, sort_by=self._sort_by, order=self._order, page=self._page, page_size=self._page_size
        )
        self._has_next = result.has_next
        self._has_prev = result.has_prev
        self._total = result.total
        self._page = result.page
        self._page_size = result.page_size
        return [item.model_dump() for item in result.items]

    async def __perform_get_one(self, result_id: int) -> dict[str, Any]:
        schema = await self._service.get_one(result_id)
        result = schema.model_dump()
        return result

    async def __perform_create(self) -> dict[str, Any]:
        output_schema = self._output_schema_cls(**self._input_values)
        input_schema = await self._service.create(output_schema)
        return input_schema.model_dump()

    async def __perform_update(self) -> dict[str, Any]:
        output_schema = self._output_schema_cls(**self._input_values)
        input_schema = await self._service.update(output_schema)
        return input_schema.model_dump()

    async def __perform_delete(self) -> None:
        output_schema = self._output_schema_cls(**self._input_values)
        await self._service.delete(output_schema.id)

    async def __open_search_results_on_button_click(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            results = await self.__perform_get_all()
            if self._view:
                self._view.replace_content(results)
                await self._close_dialog_with_delay(loading_dialog)
        except Exception as err:
            self._context.logger.error(err)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_message_dialog("no_records_found")

    async def __open_new_tab_on_row_click(self, result_id: int) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            result = await self.__perform_get_one(result_id)
            self.__open_new_read_tab(result)
            await self._close_dialog_with_delay(loading_dialog)
        except Exception as err:
            self._context.logger.error(err)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_message_dialog("record_fetch_fail")
            return None

    async def __create_and_open_new_tab_on_button_click(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            result = await self.__perform_create()
            await self._close_dialog_with_delay(loading_dialog)
            self._show_message_dialog("record_created_success")
            self.reset_view()
            self.__open_new_read_tab(result)
        except ValidationError as validation_error:
            error_messages = [self._context.texts["validation_errors"]]
            for error in validation_error.errors():
                key = error["loc"][0]
                message = error["msg"]
                error_messages.append(f"{self._context.texts[str(key)]}: {message}")
            final_message = "\n".join(error_messages)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_error_dialog(message=final_message)
        except HTTPStatusError as status_error:
            self._context.logger.error(status_error)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_error_dialog(message_key="record_create_fail")

    async def __update_and_refresh_tab_on_button_click(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            result = await self.__perform_update()
            await self._close_dialog_with_delay(loading_dialog)
            self._show_message_dialog("record_updated_success")
            if self._view:
                self._view.set_read_mode()
                self._input_values = result
                self._view.update_inputs(result)
        except ValidationError as validation_error:
            error_messages = [self._context.texts["validation_errors"]]
            for error in validation_error.errors():
                key = error["loc"][0]
                message = error["msg"]
                error_messages.append(f"{self._context.texts[str(key)]}: {message}")
            final_message = "\n".join(error_messages)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_error_dialog(message=final_message)
        except HTTPStatusError as status_error:
            self._context.logger.error(status_error)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_error_dialog(message_key="record_create_fail")

    async def __delete_and_close_tab_on_button_click(self) -> None:
        confirmation = await self._show_confirm_dialog("confirm_delete")
        if not confirmation:
            return
        loading_dialog = self._show_loading_dialog()
        try:
            await self.__perform_delete()
            await self._close_dialog_with_delay(loading_dialog)
            self._show_message_dialog("record_deleted_success")
            self._context.controllers.get("tabs_bar").on_tab_close()
        except Exception as err:
            self._context.logger.error(err)
            await self._close_dialog_with_delay(loading_dialog)
            self._show_error_dialog(message_key="record_delete_fail")

    def __open_new_read_tab(self, result: dict[str, Any]) -> None:
        new_key = f"{self._endpoint.key}_{result["id"]}"
        self._context.texts[new_key] = f"{self._context.texts[self._endpoint.key]}: {result[self._postfix]}"
        if new_key not in self._context.active_views.keys():
            controller = self._context.controllers.get_view_controller(self._endpoint.key)
            view = controller.get_new_view(data_row=result, mode=ViewMode.READ)
            self._context.active_views[new_key] = view
        view = self._context.active_views[new_key]
        self._context.controllers.get("tabs_bar").add_tab(new_key)
        self._context.controllers.get("app").render_view(view)
        view.set_read_mode()
