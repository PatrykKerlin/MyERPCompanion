from functools import partial
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import flet as ft

from utils.view_modes import ViewMode
from views.base import BaseComponent
from views.components.search_results_component import SearchResultsComponent

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController
    from schemas.base.base_schema import BaseOutputSchema
    from services.base.base_view_service import BaseViewService

TController = TypeVar("TController", bound="BaseViewController[BaseViewService, BaseView, BaseOutputSchema]")


class BaseView(BaseComponent, Generic[TController], ft.Card):
    def __init__(
        self,
        controller: TController,
        texts: dict[str, str],
        columns: int,
        data_row: dict[str, Any] | None,
        mode: ViewMode,
        controller_key: str,
    ) -> None:
        BaseComponent.__init__(self, controller, texts)
        self._mode = mode
        self._data_row = data_row
        self._controller_key = controller_key
        self._columns: list[ft.Column] = [ft.Column(expand=True) for _ in range(columns)]
        self._inputs: list[dict[str, ft.TextField | ft.Dropdown | ft.Checkbox]] = [
            {"id": ft.TextField(value=data_row["id"] if data_row else None, expand=1)}
        ]
        self._markers: list[dict[str, ft.Checkbox]] = []
        self._master_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._scrollable_wrapper = ft.ListView(controls=[self._master_column], expand=True)
        self._cancel_button = ft.Button(
            text=self._texts["cancel"],
            on_click=lambda _: self._controller.on_cancel_click(),
        )
        self._save_button = ft.ElevatedButton(
            text=self._texts["save"],
            on_click=lambda _: self._controller.on_save_click(),
            disabled=True,
        )
        self._search_button = ft.ElevatedButton(
            text=self._texts["search"],
            on_click=lambda _: self._controller.on_search_click(),
        )
        self.__set_buttons()
        self.__default_checkbox_width = 0

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def data_row(self) -> dict[str, Any] | None:
        return self._data_row

    @property
    def controller_key(self) -> str:
        return self._controller_key

    def set_visible(self, visible: bool) -> None:
        self.visible = visible

    def set_search_mode(self) -> None:
        self._mode = ViewMode.SEARCH
        for inputs, markers in zip(self._inputs, self._markers):
            for key in inputs.keys():
                if hasattr(inputs[key], "read_only"):
                    setattr(inputs[key], "read_only", False)
                inputs[key].disabled = True
                markers[key].disabled = False
                markers[key].width = self.__default_checkbox_width
                inputs[key].update()
                markers[key].update()
        self.__set_buttons()

    def set_create_mode(self) -> None:
        self._mode = ViewMode.CREATE
        self.clear_inputs()
        self.__default_checkbox_width = self._markers[0]["id"].width
        for inputs, markers in zip(self._inputs, self._markers):
            for key in inputs.keys():
                if key == "id":
                    inputs[key].disabled = True
                else:
                    inputs[key].disabled = False
                    self._controller.set_field_value(key, inputs[key].value or "")
                if hasattr(inputs[key], "read_only"):
                    setattr(inputs[key], "read_only", False)
                markers[key].disabled = True
                markers[key].width = 0
                inputs[key].update()
                markers[key].update()
        self.__set_buttons()

    def set_read_mode(self) -> None:
        self._mode = ViewMode.READ
        for inputs in self._inputs:
            for key in inputs.keys():
                if hasattr(inputs[key], "read_only"):
                    setattr(inputs[key], "read_only", True)
                self._controller.set_field_value(key, inputs[key].value or "")
                inputs[key].disabled = False
                inputs[key].update()
        self.__set_buttons()

    def set_edit_mode(self) -> None:
        self._mode = ViewMode.EDIT
        for inputs in self._inputs:
            for key in inputs.keys():
                if key == "id":
                    inputs[key].disabled = True
                else:
                    inputs[key].disabled = False
                self._controller.set_field_value(key, inputs[key].value or "")
                if hasattr(inputs[key], "read_only"):
                    setattr(inputs[key], "read_only", False)
                inputs[key].update()
        self.__set_buttons()

    def replace_content(self, data: list[dict[str, Any]] | None = None) -> None:
        if self._scrollable_wrapper.controls[0] == self._master_column and data:
            columns = [key for inputs in self._inputs for key in inputs]
            search_results = SearchResultsComponent(
                controller=self._controller,
                texts=self._texts,
                columns=columns,
                data=data,
                on_back_click=self._controller.on_back_click,
                on_row_click=self._controller.on_row_click,
            )
            self._scrollable_wrapper.controls = [search_results]
            self._mode = ViewMode.LIST
        else:
            self._scrollable_wrapper.controls = [self._master_column]
            self._mode = ViewMode.SEARCH
        self.update()

    def set_input_enabled(
        self, key: str, enabled: bool, inputs: dict[str, ft.TextField | ft.Dropdown | ft.Checkbox]
    ) -> None:
        input_field = inputs[key]
        input_field.disabled = not enabled
        input_field.update()

    def set_field_error(self, key: str, message: str | None) -> None:
        input_field = self.__get_input_field_by_key(key)
        if not input_field:
            return
        input_field.error_text = message
        input_field.update()
        self._save_button.disabled = self._controller.has_validation_errors
        self._save_button.update()

    def update_inputs(self, data_row: dict[str, Any]) -> None:
        self._data_row = data_row
        for inputs in self._inputs:
            for key, field in inputs.items():
                if key not in data_row:
                    continue
                value = data_row[key]
                if isinstance(field, ft.TextField):
                    field.value = str(value)
                elif isinstance(field, ft.Dropdown):
                    field.value = value
                elif isinstance(field, ft.Checkbox):
                    field.value = value
                field.update()

    def restore_input_data(self) -> None:
        if self._data_row:
            self.update_inputs(self._data_row)

    def clear_inputs(self) -> None:
        for inputs in self._inputs:
            for field in inputs.values():
                if isinstance(field, ft.TextField):
                    field.value = ""
                elif isinstance(field, ft.Dropdown):
                    field.value = None
                elif isinstance(field, ft.Checkbox):
                    field.value = False
                field.update()

    def clear_search_markers(self) -> None:
        for markers in self._markers:
            for marker in markers.values():
                marker.value = False
                marker.update()

    def _add_input_rows(self) -> None:
        for column, inputs, markers in zip(self._columns, self._inputs, self._markers):
            for key in inputs.keys():
                if key == "id":
                    input_field = ft.Row(
                        controls=[inputs[key], ft.Container(expand=4)],
                        expand=True,
                    )
                else:
                    input_field = inputs[key]
                inputs[key].disabled = True
                inputs[key].on_change = lambda e, key=key: self._controller.set_field_value(key, e.control.value)
                input_field.expand = 3
                label = ft.Text(value=f"{self._texts[key]}:", expand=1)
                marker = markers[key]
                row = ft.Row(
                    controls=[label, input_field, marker],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
                column.controls.append(row)

    def _add_search_markers(self) -> None:
        for inputs in self._inputs:
            markers = {
                key: ft.Checkbox(
                    tooltip=self._texts["marker_tooltip"],
                    animate_size=300,
                    value=False,
                    on_change=partial(self._controller.toggle_search_marker, key=key, inputs=inputs),
                    disabled=False if self.mode == ViewMode.SEARCH else True,
                    visible=True if self.mode == ViewMode.SEARCH else False,
                )
                for key in inputs.keys()
            }
            self._markers.append(markers)

    def __set_buttons(self) -> None:
        if self.mode in [ViewMode.EDIT, ViewMode.CREATE]:
            self._cancel_button.visible = True
            self._save_button.visible = True
            self._search_button.visible = False
        elif self.mode == ViewMode.SEARCH:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = True
        elif self.mode == ViewMode.READ:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = False
        if self._cancel_button.page:
            self._cancel_button.update()
        if self._save_button.page:
            self._save_button.update()
        if self._search_button.page:
            self._search_button.update()

    def __get_input_field_by_key(self, key: str) -> ft.TextField | ft.Dropdown | None:
        for inputs in self._inputs:
            if key in inputs:
                input_field = inputs[key]
                if isinstance(input_field, (ft.TextField, ft.Dropdown)):
                    return input_field
        return None
