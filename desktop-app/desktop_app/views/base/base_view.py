from __future__ import annotations

from collections.abc import Awaitable
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable, Generic, Sequence, TypeVar, cast

import flet as ft
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from styles.colors import AppColors
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles, ControlStyles
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.components.search_results_component import SearchResultsComponent
from views.controls.date_field_control import DateField
from views.controls.numeric_field_control import NumericField

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseView(BaseComponent, Generic[TController], ft.Card):
    _DETAIL_MODES = frozenset((ViewMode.READ, ViewMode.EDIT))

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
        self._inputs: dict[str, FieldGroup] = {}
        self._search_disabled_fields: set[str] = set()
        self._master_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._spacing_column = ft.Column(width=AppDimensions.SPACE_2XL)
        self._spacing_row = ft.Row(height=AppDimensions.SPACE_2XL)
        self._spacing_responsive_row = [ft.Container(height=ControlStyles.TEXT_FIELD_HEIGHT)]
        self._columns_row = ft.Row(
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
        )
        self._caller_view_key = caller_view_key
        self.__form_container = ft.Container(
            content=self._master_column,
            padding=ft.Padding.symmetric(
                horizontal=AppDimensions.PADDING_FORM_HORIZONTAL,
                vertical=AppDimensions.PADDING_FORM_VERTICAL,
            ),
        )
        self.__scrollable_wrapper = ft.Column(
            controls=[self.__form_container],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self._base_content = self.__scrollable_wrapper
        self.__base_label_size = base_label_size
        self.__base_input_size = base_input_size
        self.__base_columns_qty = base_columns_qty
        self.__control_base_heights: dict[int, float] = {}
        self.__search_results: list[dict[str, Any]] | None = None
        self.__dropdown_options: dict[str, list[ft.DropdownOption]] = {}
        self._cancel_button = ft.Button(
            content=self._translation.get("cancel"),
            on_click=lambda _: self._controller.on_cancel_clicked(),
            style=ButtonStyles.regular,
        )
        self._save_button = ft.Button(
            content=self._translation.get("save"),
            on_click=lambda _: self._controller.on_save_clicked(),
            disabled=False,
            style=ButtonStyles.primary_regular,
        )
        self._search_button = ft.Button(
            content=self._translation.get("search"),
            on_click=lambda _: self._controller.on_search_clicked(),
            style=ButtonStyles.primary_regular,
        )
        self._buttons_row = ft.Row(
            controls=[self._search_button, self._cancel_button, self._save_button],
            alignment=AlignmentStyles.AXIS_END,
            vertical_alignment=AlignmentStyles.CROSS_START,
            spacing=AppDimensions.BUTTON_ROW_SPACING,
        )
        self._rows = [self._columns_row, self._spacing_row, self._buttons_row]

        ft.Card.__init__(
            self,
            content=self.__scrollable_wrapper,
            expand=True,
            bgcolor=AppColors.CARD,
            shape=ft.RoundedRectangleBorder(
                radius=AppDimensions.RADIUS_MD,
                side=ft.BorderSide(
                    width=AppDimensions.TAB_CARD_BORDER_WIDTH,
                    color=self.__resolve_active_border_color(mode),
                ),
            ),
            margin=ft.Margin.only(
                top=0,
                left=AppDimensions.SPACE_2XS,
                right=AppDimensions.SPACE_2XS,
                bottom=AppDimensions.SPACE_2XS,
            ),
        )

    @property
    def view_key(self) -> View:
        return self._view_key

    @property
    def mode(self) -> ViewMode:
        return self._mode

    def _is_details_mode(self, mode: ViewMode | None = None) -> bool:
        return (mode or self._mode) in self._DETAIL_MODES

    @property
    def data_row(self) -> dict[str, Any] | None:
        return self._data_row

    @property
    def inputs(self) -> dict[str, FieldGroup]:
        return self._inputs

    @property
    def buttons_row(self) -> ft.Row:
        return self._buttons_row

    @property
    def caller_view_key(self) -> View | None:
        return self._caller_view_key

    @property
    def app_page(self) -> Any:
        return self._controller.page

    def pop_dialog(self) -> Any:
        return self._controller.pop_dialog()

    def queue_dialog(self, dialog: Any, wait_for_future: Awaitable[Any] | None = None) -> None:
        self._controller.enqueue_dialog(dialog, wait_for_future)

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
        self.shape = ft.RoundedRectangleBorder(
            radius=AppDimensions.RADIUS_MD,
            side=ft.BorderSide(
                width=AppDimensions.TAB_CARD_BORDER_WIDTH,
                color=self.__resolve_active_border_color(mode),
            ),
        )
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
        self.__set_buttons()
        BaseComponent.safe_update(self)

    @staticmethod
    def __resolve_active_border_color(mode: ViewMode) -> ft.ColorValue:
        if mode in (ViewMode.CREATE, ViewMode.EDIT):
            return AppColors.ACTIVE_BORDER_RED
        return AppColors.OUTLINE

    def set_input_state(self, control: ft.Control, enable: bool) -> None:
        self.__set_control_disabled_state(control, not enable)
        self.__set_control_read_only_state(control, not enable)
        control.update()

    def set_field_error(self, key: str, message: str | None) -> None:
        field = self._inputs[key]
        input_control = field.input.content
        if isinstance(input_control, (ft.TextField, NumericField, DateField)):
            input_control.error = message
        if isinstance(input_control, ft.Dropdown):
            input_control.error_text = message
        elif isinstance(input_control, ft.Checkbox):
            input_control.error = bool(message)
            input_control.tooltip = message
        self.__set_control_validation_height(field.input, input_control, message)
        if input_control:
            input_control.update()
        BaseComponent.safe_update(field.input)

    def clear_inputs(self) -> None:
        for key, field in self._inputs.items():
            input_control = field.input.content
            marker_control = field.marker
            marker = marker_control.content if marker_control else None
            if key in self._search_disabled_fields:
                self.__set_control_value(input_control, self.__get_default_value_for_control(input_control))
                self.__set_control_read_only_state(input_control, True)
                self.__set_control_disabled_state(input_control, True)
                self.__set_marker_state_for_non_search_mode(marker)
                self.set_field_error(key, None)
                if input_control:
                    input_control.update()
                if marker:
                    marker.update()
                continue
            if self._data_row and self._data_row.get(key) and hasattr(input_control, "value"):
                value = self._data_row[key]
                if isinstance(input_control, DateField):
                    value = self.__normalize_date_value(value)
                self.__set_control_value(input_control, value)
            else:
                self.__set_control_value(input_control, self.__get_default_value_for_control(input_control))
            if input_control:
                input_control.update()

    def reset_inputs(self) -> None:
        self._data_row = None
        self.search_results = None
        self.clear_inputs()

    def _build_field_groups(self, definitions: list[dict[str, Any]]) -> dict[str, FieldGroup]:
        return {definition["key"]: self.__build_field_group(**definition) for definition in definitions}

    def _build_grid(self, fields: dict[str, FieldGroup], inline: bool = False) -> list[ft.Control]:
        if not fields:
            return []
        if inline:
            total_columns = sum(group.columns for group in fields.values())
            inline_controls = cast(list[ft.Control], [part for group in fields.values() for part in group])
            inline_row = ft.ResponsiveRow(
                columns=total_columns,
                controls=inline_controls,
                alignment=AlignmentStyles.AXIS_START,
                vertical_alignment=self.__resolve_row_vertical_alignment(inline_controls),
            )
            return cast(list[ft.Control], [inline_row])
        rows: list[ft.Control] = []
        for group in fields.values():
            group_controls = cast(list[ft.Control], list(group))
            rows.append(
                ft.ResponsiveRow(
                    columns=group.columns,
                    controls=group_controls,
                    alignment=AlignmentStyles.AXIS_START,
                    vertical_alignment=self.__resolve_row_vertical_alignment(group_controls),
                )
            )
        return rows

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
                alignment=ControlStyles.LABEL_ALIGNMENT,
                expand=True,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
            ),
            size,
        )

    def _get_text_input(
        self,
        key: str,
        size: int,
        lines: int = 1,
        password: bool = False,
    ) -> tuple[ft.Container, int]:
        if lines > 1:
            height = (lines * ControlStyles.TEXT_FIELD_HEIGHT) + ((lines - 1) * AppDimensions.SPACE_MD)
        else:
            height = ControlStyles.TEXT_FIELD_HEIGHT

        text_field = ft.TextField(
            value="",
            on_change=lambda event: self._controller.on_value_changed(event, key),
            password=password,
            can_reveal_password=password,
            multiline=lines > 1,
            min_lines=lines,
            max_lines=lines,
            expand=True,
            height=height,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            text_vertical_align=ft.VerticalAlignment.START if lines > 1 else None,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )
        self.__register_control_base_height(text_field, height)
        if lines > 1:
            text_field.fit_parent_size = True
        return (
            ft.Container(
                content=text_field,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=height,
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
    ) -> tuple[ft.Container, int]:
        numeric_field = NumericField(
            value=value,
            step=step,
            min_value=min_value,
            max_value=max_value,
            precision=precision,
            is_float=is_float,
            on_change=lambda event: self._controller.on_value_changed(event, key),
            expand=True,
            height=ControlStyles.TEXT_FIELD_HEIGHT,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )
        self.__register_control_base_height(numeric_field, ControlStyles.TEXT_FIELD_HEIGHT)
        return (
            ft.Container(
                content=numeric_field,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
            ),
            size,
        )

    def _get_dropdown(
        self,
        key: str,
        size: int,
        options: Sequence[tuple[int | str, str]],
        callbacks: list[Callable[..., None]] | None = None,
        label: str | None = None,
        value: int | str | None = "0",
    ) -> tuple[ft.Container, int]:
        resolved_value = "0"
        if value is not None:
            value_text = str(value).strip()
            if value_text not in {"", "0"}:
                resolved_value = value_text
        dropdown = ft.Dropdown(
            options=(
                [ft.dropdown.Option(key="0", text="")]
                + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in options]
                if options
                else []
            ),
            on_select=lambda event: self._controller.on_value_changed(event, key, *(callbacks or [])),
            expand=True,
            value=resolved_value,
            label=label,
            editable=True,
            enable_search=True,
            enable_filter=True,
            height=ControlStyles.TEXT_FIELD_HEIGHT,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )
        self.__register_control_base_height(dropdown, ControlStyles.TEXT_FIELD_HEIGHT)
        return (
            ft.Container(
                content=dropdown,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
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
        date_field = DateField(
            value=value,
            min_date=min_date,
            max_date=max_date,
            read_only=read_only,
            on_change=lambda event: self._controller.on_value_changed(event, key, *(callbacks or [])),
            height=ControlStyles.TEXT_FIELD_HEIGHT,
            expand=True,
        )
        self.__register_control_base_height(date_field, ControlStyles.TEXT_FIELD_HEIGHT)
        return (
            ft.Container(
                content=date_field,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
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
        radios = [ft.Radio(value=value, label=label) for value, label in options]
        return (
            ft.Container(
                content=ft.RadioGroup(
                    content=ft.Container(
                        content=ft.Row(
                            controls=cast(list[ft.Control], radios),
                            alignment=AlignmentStyles.AXIS_SPACE_BETWEEN,
                            vertical_alignment=AlignmentStyles.CROSS_CENTER,
                            expand=True,
                            spacing=0,
                        ),
                        alignment=ControlStyles.INPUT_ALIGNMENT,
                        height=ControlStyles.TEXT_FIELD_HEIGHT,
                        padding=ControlStyles.FIELD_PADDING,
                    ),
                    value=default,
                    on_change=lambda event, key=key: self._controller.on_value_changed(event, key),
                ),
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                expand=True,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
            ),
            size,
        )

    def _get_checkbox(
        self,
        key: str,
        size: int,
        value: bool | None = None,
    ) -> tuple[ft.Container, int]:
        checkbox = ft.Checkbox(
            on_change=lambda event, key=key: self._controller.on_value_changed(event, key),
            animate_size=AppDimensions.ANIMATION_DURATION_MS,
            value=value,
            expand=True,
            shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_SM),
            border_side=ControlStyles.FIELD_BORDER_SIDE,
        )
        return (
            ft.Container(
                content=checkbox,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
                padding=ControlStyles.FIELD_PADDING,
            ),
            size,
        )

    def _get_marker(self, key: str, size: int) -> tuple[ft.Container, int]:
        marker = ft.IconButton(
            icon=ft.Icons.SEARCH_OFF,
            selected_icon=ft.Icons.SEARCH,
            selected=False,
            icon_color=AppColors.CONTROL_UNSELECTED,
            selected_icon_color=AppColors.PRIMARY,
            style=ButtonStyles.icon,
            on_click=lambda event, key=key: self.__handle_marker_click(event, key),
            tooltip=self._translation.get("check_to_search"),
            width=ControlStyles.TEXT_FIELD_HEIGHT,
            height=ControlStyles.TEXT_FIELD_HEIGHT,
            visual_density=ft.VisualDensity.COMPACT,
        )
        setattr(marker, "value", False)
        return (
            ft.Container(
                content=marker,
                col={"sm": float(size)},
                alignment=ControlStyles.INPUT_ALIGNMENT,
                height=ControlStyles.TEXT_FIELD_HEIGHT,
                padding=ControlStyles.FIELD_PADDING,
            ),
            size,
        )

    def __handle_marker_click(self, event: ft.Event[ft.IconButton], key: str) -> None:
        marker = event.control
        new_value = not bool(getattr(marker, "value", False))
        self.__set_marker_value(marker, new_value)
        marker.update()
        self._controller.on_marker_clicked(cast(ft.ControlEvent, event), key)

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
                f"Invalid layout sizes: columns={columns}, label_size={label_size}, input_size={input_size}"
            )

        return FieldGroup(
            label=self._get_label(
                key=label if label is not None else key,
                size=label_size,
                colon=colon,
            ),
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
            self.__scrollable_wrapper.controls.append(self.__form_container)
        self.__scrollable_wrapper.update()

    def __set_control_disabled_state(
        self,
        control: ft.Control | None,
        disabled: bool,
        sync_radio_option_disabled_state: bool = True,
    ) -> None:
        if control is None:
            return
        if hasattr(control, "disabled"):
            setattr(control, "disabled", disabled)
        if isinstance(control, ft.RadioGroup):
            if sync_radio_option_disabled_state:
                self.__set_radio_group_option_disabled_state(control, disabled)
            else:
                self.__set_radio_group_option_disabled_state(control, False)

    def __set_radio_group_option_disabled_state(self, radio_group: ft.RadioGroup, disabled: bool) -> None:
        container = radio_group.content
        if not isinstance(container, ft.Container) or not isinstance(container.content, ft.Row):
            return
        for item in container.content.controls:
            if isinstance(item, ft.Radio):
                item.disabled = disabled
                item.opacity = ControlStyles.DISABLED_CONTENT_OPACITY if disabled else 1.0

    def __set_control_read_only_state(self, control: ft.Control | None, read_only: bool) -> None:
        if control is None:
            return
        if hasattr(control, "read_only"):
            setattr(control, "read_only", read_only)

    def __set_control_value(self, control: ft.Control | None, value: Any) -> None:
        if control is None or not hasattr(control, "value"):
            return
        setattr(control, "value", value)

    def __resolve_row_vertical_alignment(self, controls: Sequence[ft.Control]) -> ft.CrossAxisAlignment:
        for control in controls:
            if not isinstance(control, ft.Container):
                continue
            control_height = control.height
            if isinstance(control_height, (int, float)) and control_height > ControlStyles.TEXT_FIELD_HEIGHT:
                return AlignmentStyles.CROSS_START
        return AlignmentStyles.CROSS_CENTER

    def __register_control_base_height(self, control: ft.Control, height: int | float) -> None:
        self.__control_base_heights[id(control)] = float(height)

    def __set_control_validation_height(
        self,
        input_container: ft.Container,
        control: ft.Control | None,
        message: str | None,
    ) -> None:
        if control is None:
            return
        base_height = self.__control_base_heights.get(id(control))
        if base_height is None:
            return
        extra_height = ControlStyles.VALIDATION_ERROR_EXTRA_HEIGHT if message else 0
        target_height = base_height + extra_height
        set_validation_height = getattr(control, "set_validation_height", None)
        if callable(set_validation_height):
            set_validation_height(target_height)
        elif hasattr(control, "height"):
            setattr(control, "height", target_height)
        input_container.height = target_height

    def __set_marker_state_for_non_search_mode(self, marker: ft.Control | None) -> None:
        if marker is None:
            return
        if hasattr(marker, "visible"):
            setattr(marker, "visible", False)
        if hasattr(marker, "disabled"):
            setattr(marker, "disabled", True)
        self.__set_marker_value(marker, False)
        if hasattr(marker, "width"):
            setattr(marker, "width", 0)

    def __set_marker_state_for_search_mode(self, marker: ft.Control | None, selected: bool) -> None:
        if marker is None:
            return
        if hasattr(marker, "visible"):
            setattr(marker, "visible", True)
        if hasattr(marker, "disabled"):
            setattr(marker, "disabled", False)
        self.__set_marker_value(marker, selected)
        if hasattr(marker, "width"):
            if isinstance(marker, ft.IconButton):
                setattr(marker, "width", ControlStyles.TEXT_FIELD_HEIGHT)
            else:
                setattr(marker, "width", None)

    def __set_marker_value(self, marker: ft.Control, selected: bool) -> None:
        if hasattr(marker, "value"):
            setattr(marker, "value", selected)
        if isinstance(marker, ft.IconButton):
            marker.selected = selected

    def __get_default_value_for_control(self, control: ft.Control | None) -> Any:
        if isinstance(control, ft.TextField):
            return ""
        if isinstance(control, ft.Dropdown):
            return "0"
        if isinstance(control, ft.Checkbox):
            return False
        if isinstance(control, NumericField):
            return 0
        if isinstance(control, DateField):
            return None
        return None

    def __set_search_mode(self) -> None:
        selected_inputs = self._controller.search_params.selected_inputs
        input_values = self._controller.search_params.input_values
        for key, field in self._inputs.items():
            marker_control = field.marker
            marker = marker_control.content if marker_control else None
            if key in self._search_disabled_fields:
                self.__set_marker_state_for_non_search_mode(marker)
                if marker:
                    marker.update()
                input_control = field.input.content
                self.__set_control_read_only_state(input_control, True)
                self.__set_control_disabled_state(input_control, True)
                if input_control:
                    input_control.update()
                continue
            input_control = field.input.content
            marker_selected = bool(getattr(marker, "value", False)) if marker else False
            is_selected = key in selected_inputs or marker_selected
            if is_selected:
                selected_inputs.add(key)
            else:
                selected_inputs.discard(key)
            if isinstance(input_control, ft.Dropdown):
                self.__restore_dropdown_options(input_control, key)
            if hasattr(input_control, "value") and key in input_values:
                value = input_values.get(key)
                if value is None:
                    value = self.__get_default_value_for_control(input_control)
                if isinstance(input_control, DateField):
                    value = self.__normalize_date_value(value)
                self.__set_control_value(input_control, value)
            self.__set_control_read_only_state(input_control, not is_selected)
            self.__set_control_disabled_state(input_control, not is_selected)
            self.__set_marker_state_for_search_mode(marker, is_selected)
            self.set_field_error(key, None)
            if input_control:
                input_control.update()
            if marker:
                marker.update()
        self.__toggle_search_results()

    def __set_create_mode(self) -> None:
        self.clear_inputs()
        for key, field in self._inputs.items():
            input_control = field.input.content
            marker_control = field.marker
            marker = marker_control.content if marker_control else None
            input_disabled = key in self._controller.meta_fields
            self.__set_control_disabled_state(input_control, input_disabled)
            if (
                isinstance(input_control, ft.Dropdown)
                and self._data_row
                and self._caller_view_key
                and key in self._data_row
                and self._data_row.get(key) is not None
            ):
                self.__limit_dropdown_options(input_control, key)
            self.__set_control_read_only_state(input_control, key in self._controller.meta_fields)
            self.__set_marker_state_for_non_search_mode(marker)
            if hasattr(input_control, "value"):
                self._controller.set_field_value(key, getattr(input_control, "value", ""))
            if input_control:
                input_control.update()
            if marker:
                marker.update()

    def __set_list_mode(self) -> None:
        self.__toggle_search_results()

    def __set_read_mode(self) -> None:
        for key, field in self._inputs.items():
            input_control = field.input.content
            marker_control = field.marker
            marker = marker_control.content if marker_control else None
            self.__set_control_read_only_state(input_control, True)
            input_disabled = not isinstance(input_control, (ft.TextField, ft.Dropdown, NumericField, DateField))
            self.__set_control_disabled_state(input_control, input_disabled, sync_radio_option_disabled_state=False)
            if isinstance(input_control, ft.Dropdown) and self._data_row:
                self.__limit_dropdown_options(input_control, key)
            self.__set_marker_state_for_non_search_mode(marker)
            if self._data_row and hasattr(input_control, "value"):
                if key in self._data_row:
                    value = self._data_row.get(key)
                else:
                    value = self.__get_default_value_for_control(input_control)
                if isinstance(input_control, DateField):
                    value = self.__normalize_date_value(value)
                self.__set_control_value(input_control, value)
            if input_control:
                input_control.update()
            if marker:
                marker.update()

    def __set_edit_mode(self) -> None:
        for key, field in self._inputs.items():
            input_control = field.input.content
            input_disabled = key in self._controller.meta_fields
            self.__set_control_disabled_state(input_control, input_disabled)
            self.__set_control_read_only_state(input_control, False)
            if isinstance(input_control, ft.Dropdown):
                self.__restore_dropdown_options(input_control, key)
            if hasattr(input_control, "value"):
                self._controller.set_field_value(key, getattr(input_control, "value", ""))
            if input_control:
                input_control.update()

    def __set_buttons(self) -> None:
        if self._mode in [ViewMode.EDIT, ViewMode.CREATE]:
            self._cancel_button.visible = True
            self._save_button.visible = True
            self._search_button.visible = False
        elif self._mode == ViewMode.SEARCH:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = True
        elif self._mode == ViewMode.READ:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = False
        if self._cancel_button.page:
            self._cancel_button.update()
        if self._save_button.page:
            self._save_button.update()
        if self._search_button.page:
            self._search_button.update()

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

    def __limit_dropdown_options(self, dropdown: ft.Dropdown, key: str) -> None:
        if not self._data_row:
            return
        source_options = self.__dropdown_options.get(key)
        if source_options is None:
            source_options = list(dropdown.options)
            self.__dropdown_options[key] = source_options
        value = self._data_row.get(key)
        if value in {None, "", "0", 0}:
            dropdown.options = [ft.dropdown.Option(key="0", text="")]
            dropdown.value = "0"
            return
        value_key = str(value)
        matching_option = next((option for option in source_options if option.key == value_key), None)
        if matching_option is None:
            matching_option = ft.dropdown.Option(key=value_key, text=value_key)
        dropdown.options = [matching_option]
        dropdown.value = value_key

    def __restore_dropdown_options(self, dropdown: ft.Dropdown, key: str) -> None:
        if self.__dropdown_options.get(key) is not None:
            dropdown.options = self.__dropdown_options[key]
