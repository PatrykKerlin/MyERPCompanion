from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

import flet as ft

from utils.enums import ViewMode
from utils.view_fields import FieldGroup
from views.base.base_component import BaseComponent
from views.components.integer_field_component import IntegerField
from views.components.search_results_component import SearchResultsComponent

if TYPE_CHECKING:
    from utils.translation import Translation
    from controllers.base.base_view_controller import BaseViewController
    from schemas.base.base_schema import BaseStrictSchema, BasePlainSchema
    from services.base.base_service import BaseService

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseView(BaseComponent, Generic[TController], ft.Card):
    def __init__(
        self,
        controller: TController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
    ) -> None:
        BaseComponent.__init__(self, controller, translation)
        self._mode = mode
        self._view_key = key
        self._data_row = data_row
        self._inputs: dict[str, FieldGroup] = {}
        self._master_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._scrollable_wrapper = ft.ListView(controls=[self._master_column], expand=True)
        self._cancel_button = ft.Button(
            text=self._translation.get("cancel"),
            on_click=lambda _: self._controller.on_cancel_clicked(),
        )
        self._save_button = ft.ElevatedButton(
            text=self._translation.get("save"),
            on_click=lambda _: self._controller.on_save_clicked(),
            disabled=True,
        )
        self._search_button = ft.ElevatedButton(
            text=self._translation.get("search"),
            on_click=lambda _: self._controller.on_search_clicked(),
        )
        self._meta_fields = {
            "id": FieldGroup(
                label=self._get_label("id", 5),
                input=self._get_text_input("id", 2),
                marker=self._get_marker("id", 5),
            ),
            "created_by": FieldGroup(
                label=self._get_label("created_by", 5),
                input=self._get_text_input("created_by", 2),
                marker=self._get_marker("created_by", 5),
            ),
            "created_at": FieldGroup(
                label=self._get_label("created_at'", 5),
                input=self._get_text_input("created_at", 6),
                marker=self._get_marker("created_at", 1),
            ),
            "modified_by": FieldGroup(
                label=self._get_label("modified_by", 5),
                input=self._get_text_input("modified_by", 2),
                marker=self._get_marker("modified_by", 5),
            ),
            "modified_at": FieldGroup(
                label=self._get_label("modified_at", 5),
                input=self._get_text_input("modified_at", 6),
                marker=self._get_marker("modified_at", 1),
            ),
        }
        self.__base_height = 56
        self.__base_aligment = ft.alignment.center_left

    @property
    def view_key(self) -> str:
        return self._view_key

    @property
    def mode(self) -> ViewMode:
        return self._mode

    @property
    def data_row(self) -> dict[str, Any] | None:
        return self._data_row

    @property
    def inputs(self) -> dict[str, FieldGroup]:
        return self._inputs

    def did_mount(self):
        self.set_mode(self._mode)
        return super().did_mount()

    def set_mode(self, mode: ViewMode) -> None:
        self._mode = mode
        match mode:
            case ViewMode.SEARCH:
                self.__set_search_mode()
            case ViewMode.LIST:
                self.__set_list_mode()
            case ViewMode.READ:
                self.__set_read_mode()
            case ViewMode.CREATE:
                self.__set_create_mode()
            case ViewMode.EDIT:
                self.__set_edit_mode()
        self.__set_buttons()

    def set_input_state(self, input: ft.Control, enable: bool) -> None:
        input.disabled = not enable
        input.update()

    def set_save_button_state(self, enable: bool) -> None:
        self._save_button.disabled = not enable
        self._save_button.update()

    def set_field_error(self, key: str, message: str | None) -> None:
        field = self._inputs[key]
        if isinstance(field.input.content, (ft.TextField, ft.Dropdown, IntegerField)):
            field.input.content.error_text = message
        elif isinstance(field.input.content, ft.Checkbox):
            field.input.content.is_error = bool(message)
            field.input.content.tooltip = message
        if field.input.content:
            field.input.content.update()

    def toggle_search_results(self, data: list[dict[str, Any]] | None = None) -> None:
        if data:
            columns = ["id"] + [key for key in self._inputs.keys() if key != "id"]
            search_results = SearchResultsComponent(
                controller=self._controller, translation=self._translation, columns=columns, data=data
            )
            self._scrollable_wrapper.controls.clear()
            self._scrollable_wrapper.controls.append(search_results)
            self._mode = ViewMode.LIST
        else:
            self._scrollable_wrapper.controls.clear()
            self._scrollable_wrapper.controls.append(self._master_column)
            self._mode = ViewMode.SEARCH
        self._scrollable_wrapper.update()

    def _get_label(self, key: str, size: int) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.Text(value=f"{self._translation.get(key)}:"),
                col={"sm": float(size)},
                alignment=self.__base_aligment,
                height=self.__base_height,
            ),
            size,
        )

    def _get_text_input(self, key: str, size: int, lines: int = 1) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.TextField(
                    value="",
                    on_change=lambda event: self._controller.on_text_changed(event, key),
                    min_lines=lines,
                    max_lines=lines,
                ),
                col={"sm": float(size)},
                alignment=self.__base_aligment,
                height=self.__base_height * lines,
            ),
            size,
        )

    def _get_marker(self, key: str, size: int) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.Checkbox(
                    on_change=lambda event, key=key: self._controller.on_marker_clicked(event, key),
                    tooltip=self._translation.get("check_to_search"),
                    animate_size=300,
                    value=False,
                ),
                col={"sm": float(size)},
                alignment=self.__base_aligment,
                height=self.__base_height,
            ),
            size,
        )

    def _build_grid(self, fields: dict[str, FieldGroup]) -> list[ft.ResponsiveRow]:
        return [
            ft.ResponsiveRow(
                columns=group.columns,
                controls=[part for part in group],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
            for group in fields.values()
        ]

    def __set_search_mode(self) -> None:
        for key, field in self._inputs.items():
            input = field.input.content
            marker = field.marker.content
            if hasattr(input, "read_only"):
                setattr(input, "read_only", False)
            if hasattr(input, "disabled"):
                setattr(input, "disabled", True)
            if hasattr(marker, "disabled"):
                setattr(marker, "disabled", False)
            if hasattr(marker, "width"):
                setattr(marker, "width", None)
            self.set_field_error(key, None)
            if input:
                input.update()
            if marker:
                marker.update()

    def __set_list_mode(self) -> None:
        pass

    def __set_read_mode(self) -> None:
        for key, field in self._inputs.items():
            if hasattr(field.input.control, "read_only"):
                setattr(field.input.control, "read_only", True)
            if self._data_row:
                field.input.control.value = self._data_row[key]
            field.input.control.disabled = False
            field.marker.control.disabled = True
            field.marker.control.width = 0
            field.input.control.update()
            field.marker.control.update()

    def __set_create_mode(self) -> None:
        self.__clear_inputs()
        for key, field in self._inputs.items():
            if key in self._meta_fields.keys():
                field.input.control.disabled = True
            else:
                field.input.control.disabled = False
            if hasattr(field.input.control, "read_only"):
                setattr(field.input.control, "read_only", False)
            field.marker.control.disabled = True
            field.marker.control.width = 0
            self._controller.set_field_value(key, field.input.control.value)
            field.input.control.update()
            field.marker.control.update()

    def __set_edit_mode(self) -> None:
        for key, field in self._inputs.items():
            if key in self._meta_fields.keys():
                field.input.control.disabled = True
            else:
                field.input.control.disabled = False
            if hasattr(field.input.control, "read_only"):
                setattr(field.input.control, "read_only", False)
            self._controller.set_field_value(key, field.input.control.value)
            field.input.control.update()

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

    def __clear_inputs(self) -> None:
        for field in self._inputs.values():
            if isinstance(field.input.control, ft.TextField):
                field.input.control.value = ""
            elif isinstance(field.input.control, ft.Dropdown):
                field.input.control.value = None
            elif isinstance(field.input.control, ft.Checkbox):
                field.input.control.value = False
            field.input.control.update()


# @property
# def mode(self) -> str:
#     return self._mode

# @property
# def data_row(self) -> dict[str, Any] | None:
#     return self._data_row

# @property
# def controller_key(self) -> str:
#     return self._controller_key

# def set_visible(self, visible: bool) -> None:
#     self.visible = visible

# def update_inputs(self, data_row: dict[str, Any]) -> None:
#     self._data_row = data_row
#     for inputs in self._inputs:
#         for key, field in inputs.items():
#             if key not in data_row:
#                 continue
#             value = data_row[key]
#             if isinstance(field, ft.TextField):
#                 field.value = str(value)
#             elif isinstance(field, ft.Dropdown):
#                 field.value = value
#             elif isinstance(field, ft.Checkbox):
#                 field.value = value
#             field.update()

# def clear_search_markers(self) -> None:
#     for markers in self._markers:
#         for marker in markers.values():
#             marker.value = False
#             marker.update()
