from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Sequence, TypeVar, cast
from datetime import date, datetime

import flet as ft

from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from views.base.base_component import BaseComponent
from views.controls.date_field_control import DateField
from views.controls.numeric_field_control import NumericField
from views.components.search_results_component import SearchResultsComponent
from utils.translation import Translation
from schemas.base.base_schema import BaseStrictSchema, BasePlainSchema
from services.base.base_service import BaseService

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseView(BaseComponent, Generic[TController], ft.Container):
    def __init__(
        self,
        controller: TController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        base_label_size: int,
        base_input_size: int,
        base_columns_qty: int = 12,
        caller_view_key: View | None = None,
    ) -> None:
        BaseComponent.__init__(self, controller, translation)
        self._mode = mode
        self._view_key = view_key
        self._data_row = data_row
        self._base_alignment = ft.Alignment.CENTER_LEFT
        self._inputs: dict[str, FieldGroup] = {}
        self._search_disabled_fields: set[str] = set()
        self._master_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._spacing_column = ft.Column(width=25)
        self._spacing_row = ft.Row(height=25)
        self._spacing_responsive_row = [
            ft.ResponsiveRow(controls=[ft.Container(content=ft.TextField(disabled=True), opacity=0.0, col={"sm": 1})])
        ]
        self._columns_row = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self._caller_view_key = caller_view_key
        self.__scrollable_wrapper = ft.Column(
            controls=[self._master_column],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self._base_content = self.__scrollable_wrapper
        self.__base_label_size = base_label_size
        self.__base_input_size = base_input_size
        self.__base_columns_qty = base_columns_qty
        self.__search_results: list[dict[str, Any]] | None = None
        self.__dropdown_options: dict[str, list[ft.DropdownOption]] = {}

        ft.Container.__init__(self, content=self.__scrollable_wrapper, expand=True)

    @property
    def view_key(self) -> View:
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

    @property
    def caller_view_key(self) -> View | None:
        return self._caller_view_key

    @property
    def search_results(self) -> list[dict[str, Any]] | None:
        return self.__search_results

    @search_results.setter
    def search_results(self, value: list[dict[str, Any]] | None) -> None:
        self.__search_results = value
        if self._mode == ViewMode.LIST:
            self.__toggle_search_results()

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
            case ViewMode.STATIC:
                return

    def set_input_state(self, input: ft.Control, enable: bool) -> None:
        if hasattr(input, "disabled"):
            setattr(input, "disabled", not enable)
        if hasattr(input, "read_only"):
            setattr(input, "read_only", not enable)
        input.update()

    def set_field_error(self, key: str, message: str | None) -> None:
        field = self._inputs[key]
        if isinstance(field.input.content, (ft.TextField, NumericField)):
            field.input.content.error = message
        if isinstance(field.input.content, ft.Dropdown):
            field.input.content.error_text = message
        elif isinstance(field.input.content, ft.Checkbox):
            field.input.content.error = bool(message)
            field.input.content.tooltip = message
        if field.input.content:
            field.input.content.update()

    def clear_inputs(self) -> None:
        for key, field in self._inputs.items():
            input = field.input.content
            if key in self._search_disabled_fields:
                marker = field.marker.content
                if isinstance(input, ft.TextField):
                    input.value = ""
                elif isinstance(input, ft.Dropdown):
                    input.value = "0"
                elif isinstance(input, ft.Checkbox):
                    input.value = False
                elif isinstance(input, NumericField):
                    input.value = 0
                elif isinstance(input, DateField):
                    input.value = None
                if hasattr(input, "read_only"):
                    setattr(input, "read_only", True)
                if hasattr(input, "disabled"):
                    setattr(input, "disabled", True)
                if hasattr(marker, "disabled"):
                    setattr(marker, "disabled", True)
                if hasattr(marker, "value"):
                    setattr(marker, "value", False)
                if hasattr(marker, "width"):
                    setattr(marker, "width", 0)
                self.set_field_error(key, None)
                if input:
                    input.update()
                if marker:
                    marker.update()
                continue
            if self._data_row and self._data_row.get(key) and hasattr(input, "value"):
                value = self._data_row[key]
                if isinstance(input, DateField):
                    value = self.__normalize_date_value(value)
                setattr(input, "value", value)
            elif isinstance(input, ft.TextField):
                input.value = ""
            elif isinstance(input, ft.Dropdown):
                input.value = "0"
            elif isinstance(input, ft.Checkbox):
                input.value = False
            elif isinstance(input, NumericField):
                input.value = 0
            elif isinstance(input, DateField):
                input.value = None
            if input:
                input.update()

    def _build_field_groups(self, definitions: list[dict[str, Any]]) -> dict[str, FieldGroup]:
        return {definition["key"]: self.__build_field_group(**definition) for definition in definitions}

    def _build_grid(self, fields: dict[str, FieldGroup], inline: bool = False) -> list[ft.Control]:
        if not fields:
            return []
        if inline:
            total_columns = sum(group.columns for group in fields.values())
            inline_controls = [part for group in fields.values() for part in group]
            return [
                ft.ResponsiveRow(
                    columns=total_columns,
                    controls=cast(list[ft.Control], inline_controls),
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            ]
        return [
            ft.ResponsiveRow(
                columns=group.columns,
                controls=[part for part in group],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
            for group in fields.values()
        ]

    def _add_to_inputs(self, *fields: dict[str, FieldGroup]) -> None:
        for field in fields:
            self._inputs.update(field)

    def _get_meta_grid(self, label_size: int, id_size: int, text_size: int, columns: int = 12) -> list[ft.Control]:
        free_columns = columns - label_size
        id_marker_size = free_columns - id_size
        text_marker_size = free_columns - text_size
        meta_fields = {
            "id": FieldGroup(
                label=self._get_label("id", label_size),
                input=self._get_text_input("id", id_size),
                marker=self._get_marker("id", id_marker_size),
            ),
            "created_by_username": FieldGroup(
                label=self._get_label("created_by_username", label_size),
                input=self._get_text_input("created_by_username", text_size),
                marker=self._get_marker("created_by_username", text_marker_size),
            ),
            "created_at": FieldGroup(
                label=self._get_label("created_at", label_size),
                input=self._get_text_input("created_at", text_size),
                marker=self._get_marker("created_at", text_marker_size),
            ),
            "modified_by_username": FieldGroup(
                label=self._get_label("modified_by_username", label_size),
                input=self._get_text_input("modified_by_username", text_size),
                marker=self._get_marker("modified_by_username", text_marker_size),
            ),
            "modified_at": FieldGroup(
                label=self._get_label("modified_at", label_size),
                input=self._get_text_input("modified_at", text_size),
                marker=self._get_marker("modified_at", text_marker_size),
            ),
        }
        self._inputs.update(meta_fields)

        return self._build_grid(meta_fields)

    def _get_label(self, key: str, size: int, colon: bool = True) -> tuple[ft.Container, int]:
        text_value = self._translation.get(key)
        if colon and not text_value.endswith(":"):
            text_value = f"{text_value}:"
        return (
            ft.Container(
                content=ft.Text(value=text_value),
                col={"sm": float(size)},
                alignment=self._base_alignment,
                expand=True,
            ),
            size,
        )

    def _get_text_input(self, key: str, size: int, lines: int = 1) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.TextField(
                    value="",
                    on_change=lambda event: self._controller.on_value_changed(event, key),
                    min_lines=lines,
                    max_lines=lines,
                    expand=True,
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
            ),
            size,
        )

    def _get_password_input(self, key: str, size: int) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.TextField(
                    value="",
                    password=True,
                    can_reveal_password=True,
                    on_change=lambda event: self._controller.on_value_changed(event, key),
                    expand=True,
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
            ),
            size,
        )

    def _get_numeric_input(
        self,
        key: str,
        size: int,
        value: int | float = 0,
        step: int | float = 1,
        precision: int = 2,
        min_value: int | float | None = 0,
        max_value: int | float | None = None,
        is_float: bool = False,
        expand: int | bool | None = True,
    ) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=NumericField(
                    value=value,
                    step=step,
                    min_value=min_value,
                    max_value=max_value,
                    precision=precision,
                    is_float=is_float,
                    on_change=lambda event: self._controller.on_value_changed(event, key),
                    expand=expand,
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
            ),
            size,
        )

    def _get_dropdown(
        self,
        key: str,
        size: int,
        options: Sequence[tuple[int | str, str]],
        callbacks: list[Callable[..., None]] | None = None,
    ) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.Dropdown(
                    options=(
                        [ft.dropdown.Option(key="0", text="")]
                        + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in options]
                        if options
                        else []
                    ),
                    on_select=lambda event: self._controller.on_value_changed(event, key, *(callbacks or [])),
                    expand=True,
                    value="0",
                    editable=True,
                    enable_search=True,
                    enable_filter=True,
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
            ),
            size,
        )

    def _get_date_picker(
        self,
        key: str,
        size: int,
        callbacks: list[Callable[..., None]] | None = None,
        value: date | None = None,
        min_date: date | None = None,
        max_date: date | None = None,
        read_only: bool = True,
    ) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=DateField(
                    value=value,
                    min_date=min_date,
                    max_date=max_date,
                    read_only=read_only,
                    on_change=lambda event: self._controller.on_value_changed(event, key, *(callbacks or [])),
                    expand=True,
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
            ),
            size,
        )

    def _get_radio_group(
        self,
        key: str,
        size: int,
        options: list[tuple[str, str]],
        default: str | None = None,
    ) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.RadioGroup(
                    content=ft.Row(
                        controls=[ft.Radio(value=value, label=label) for value, label in options],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        spacing=0,
                    ),
                    value=default,
                    on_change=lambda event, key=key: self._controller.on_value_changed(event, key),
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
                expand=True,
            ),
            size,
        )

    def _get_checkbox(self, key: str, size: int, value: bool | None = None) -> tuple[ft.Container, int]:
        return (
            ft.Container(
                content=ft.Checkbox(
                    on_change=lambda event, key=key: self._controller.on_value_changed(event, key),
                    animate_size=300,
                    value=value,
                    shape=ft.CircleBorder(),
                ),
                col={"sm": float(size)},
                alignment=self._base_alignment,
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
                alignment=self._base_alignment,
            ),
            size,
        )

    def __build_field_group(
        self,
        input: Callable[..., Any],
        key: str,
        label: str | None = None,
        label_size: int | None = None,
        input_size: int | None = None,
        columns: int | None = None,
        colon: bool = True,
        **kwargs: Any,
    ) -> FieldGroup:
        label_size = label_size if label_size is not None else self.__base_label_size
        input_size = input_size if input_size is not None else self.__base_input_size
        columns = columns if columns is not None else self.__base_columns_qty
        marker_size = columns - label_size - input_size

        if marker_size < 1:
            raise ValueError(
                f"Invalid layout sizes: columns={columns}, " f"label_size={label_size}, input_size={input_size}"
            )

        return FieldGroup(
            label=self._get_label(key=label if label is not None else key, size=label_size, colon=colon),
            input=input(key, size=input_size, **kwargs),
            marker=self._get_marker(key, size=marker_size),
        )

    def __toggle_search_results(self) -> None:
        if self._mode == ViewMode.LIST and self.__search_results:
            available = ["id"] + [key for key in self._inputs.keys() if key != "id"]
            columns = self._controller.get_search_result_columns(available)
            search_results = SearchResultsComponent(
                controller=self._controller, translation=self._translation, columns=columns, data=self.__search_results
            )
            self.__scrollable_wrapper.controls.clear()
            self.__scrollable_wrapper.controls.append(search_results)
        elif self._mode == ViewMode.SEARCH:
            self.__scrollable_wrapper.controls.clear()
            self.__scrollable_wrapper.controls.append(self._master_column)
        self.__scrollable_wrapper.update()

    def __set_search_mode(self) -> None:
        selected_inputs = self._controller.search_params.selected_inputs
        input_values = self._controller.search_params.input_values
        for key, field in self._inputs.items():
            if key in self._search_disabled_fields:
                marker = field.marker.content
                if hasattr(marker, "disabled"):
                    setattr(marker, "disabled", True)
                if hasattr(marker, "value"):
                    setattr(marker, "value", False)
                if hasattr(marker, "width"):
                    setattr(marker, "width", 0)
                if marker:
                    marker.update()
                
                input = field.input.content
                if hasattr(input, "read_only"):
                    setattr(input, "read_only", True)
                if hasattr(input, "disabled"):
                    setattr(input, "disabled", True)
                if input:
                    input.update()
                continue
            input = field.input.content
            marker = field.marker.content
            marker_selected = bool(getattr(marker, "value", False)) if marker else False
            is_selected = key in selected_inputs or marker_selected
            if is_selected:
                selected_inputs.add(key)
            else:
                selected_inputs.discard(key)
            if isinstance(input, ft.Dropdown):
                self.__restore_dropdown_options(input, key)
            if hasattr(input, "value"):
                if key in input_values:
                    value = input_values.get(key)
                    if value is None:
                        if isinstance(input, ft.TextField):
                            value = ""
                        elif isinstance(input, ft.Dropdown):
                            value = "0"
                        elif isinstance(input, ft.Checkbox):
                            value = False
                        elif isinstance(input, NumericField):
                            value = 0
                        elif isinstance(input, DateField):
                            value = None
                    if isinstance(input, DateField):
                        value = self.__normalize_date_value(value)
                    setattr(input, "value", value)
            if hasattr(input, "read_only"):
                setattr(input, "read_only", not is_selected)
            if hasattr(input, "disabled"):
                setattr(input, "disabled", not is_selected)
            if hasattr(marker, "disabled"):
                setattr(marker, "disabled", False)
            if hasattr(marker, "value"):
                setattr(marker, "value", is_selected)
            if hasattr(marker, "width"):
                setattr(marker, "width", None)
            self.set_field_error(key, None)
            if input:
                input.update()
            if marker:
                marker.update()
        self.__toggle_search_results()

    def __set_create_mode(self) -> None:
        self.clear_inputs()
        for key, field in self._inputs.items():
            input = field.input.content
            marker = field.marker.content
            if hasattr(input, "disabled"):
                if key in self._controller.meta_fields:
                    setattr(input, "disabled", True)
                else:
                    setattr(input, "disabled", False)
                if (
                    isinstance(input, ft.Dropdown)
                    and self._data_row
                    and self._caller_view_key
                    and key in self._data_row
                    and self._data_row.get(key) is not None
                ):
                    self.__limit_dropdown_options(input, key)
            if hasattr(input, "read_only"):
                if key in self._controller.meta_fields:
                    setattr(input, "read_only", True)
                else:
                    setattr(input, "read_only", False)
            if hasattr(marker, "disabled"):
                setattr(marker, "disabled", True)
            if hasattr(marker, "width"):
                setattr(marker, "width", 0)
            if hasattr(input, "value"):
                self._controller.set_field_value(key, getattr(input, "value", ""))
            if input:
                input.update()
            if marker:
                marker.update()

    def __set_list_mode(self) -> None:
        self.__toggle_search_results()

    def __set_read_mode(self) -> None:
        for key, field in self._inputs.items():
            input = field.input.content
            marker = field.marker.content
            if hasattr(input, "read_only"):
                setattr(input, "read_only", True)
            if hasattr(input, "disabled"):
                if isinstance(input, (ft.TextField, ft.Dropdown, NumericField, DateField)):
                    setattr(input, "disabled", False)
                else:
                    setattr(input, "disabled", True)
                if isinstance(input, ft.Dropdown) and self._data_row:
                    self.__limit_dropdown_options(input, key)
            if hasattr(marker, "disabled"):
                setattr(marker, "disabled", True)
            if hasattr(marker, "width"):
                setattr(marker, "width", 0)
            if self._data_row and hasattr(input, "value"):
                if key in self._data_row:
                    value = self._data_row.get(key)
                else:
                    if isinstance(input, ft.TextField):
                        value = ""
                    elif isinstance(input, NumericField):
                        value = 0
                    elif isinstance(input, DateField):
                        value = None
                    elif isinstance(input, ft.Checkbox):
                        value = False
                    else:
                        value = None
                if isinstance(input, DateField):
                    value = self.__normalize_date_value(value)
                setattr(input, "value", value)
            if input:
                input.update()
            if marker:
                marker.update()

    def __set_edit_mode(self) -> None:
        for key, field in self._inputs.items():
            input = field.input.content
            if hasattr(input, "disabled"):
                if key in self._controller.meta_fields:
                    setattr(input, "disabled", True)
                else:
                    setattr(input, "disabled", False)
            if hasattr(input, "read_only"):
                setattr(input, "read_only", False)
            if isinstance(input, ft.Dropdown):
                self.__restore_dropdown_options(input, key)
            if hasattr(input, "value"):
                self._controller.set_field_value(key, getattr(input, "value", ""))
            if input:
                input.update()

    def __normalize_date_value(self, value: Any) -> date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                return None
        return None

    def __limit_dropdown_options(self, input: ft.Dropdown, key: str) -> None:
        if not self._data_row:
            return
        source_options = self.__dropdown_options.get(key)
        if source_options is None:
            source_options = list(input.options)
            self.__dropdown_options[key] = source_options
        value = self._data_row.get(key)
        if value in {None, "", "0", 0}:
            input.options = [ft.dropdown.Option(key="0", text="")]
            input.value = "0"
            return
        value_key = str(value)
        matching_option = next((option for option in source_options if option.key == value_key), None)
        if matching_option is None:
            matching_option = ft.dropdown.Option(key=value_key, text=value_key)
        input.options = [matching_option]
        input.value = value_key

    def __restore_dropdown_options(self, input: ft.Dropdown, key: str) -> None:
        if self.__dropdown_options.get(key) is not None:
            input.options = self.__dropdown_options[key]
