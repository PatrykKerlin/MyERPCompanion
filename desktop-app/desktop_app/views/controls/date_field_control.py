from datetime import date, datetime, timedelta
from types import SimpleNamespace
from typing import Callable, cast

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles, ControlStyles
from views.base.base_component import BaseComponent


class DateField(ft.Row):
    def __init__(
        self,
        value: date | None = None,
        min_date: date | None = None,
        max_date: date | None = None,
        date_format: str = "%Y-%m-%d",
        height: int | float | None = None,
        width: float | None = None,
        expand: int | bool | None = None,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> None:
        resolved_height = height or ControlStyles.TEXT_FIELD_HEIGHT
        super().__init__(
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
            height=resolved_height,
            width=width,
            expand=expand,
            spacing=AppDimensions.SPACE_XS,
        )
        self.__on_change = on_change
        self.__format = date_format
        self.__value = value
        self.__min = min_date
        self.__max = max_date
        self.__read_only = read_only

        self.__text_field = ft.TextField(
            value=self.__format_value(self.__value),
            read_only=True,
            expand=True,
            text_align=ft.TextAlign.CENTER,
            height=resolved_height,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )

        self.__picker = ft.DatePicker(on_change=self.__handle_picker_change)
        if self.__min is not None:
            self.__picker.first_date = self.__min
        if self.__max is not None:
            self.__picker.last_date = self.__max
        if self.__value is not None:
            self.__picker.value = self.__value

        self.__open_button = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.__open_picker,
            disabled=self.__read_only,
            width=AppDimensions.ICON_BUTTON_WIDTH,
            style=ButtonStyles.icon,
        )
        self.__clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            on_click=self.__clear_date,
            disabled=self.__read_only or self.__value is None,
            width=AppDimensions.ICON_BUTTON_WIDTH,
            style=ButtonStyles.icon,
        )

        self.controls = [
            self.__picker,
            ft.Container(content=self.__open_button, alignment=AlignmentStyles.TOP_CENTER),
            self.__text_field,
            ft.Container(content=self.__clear_button, alignment=AlignmentStyles.TOP_CENTER),
        ]

    @property
    def value(self) -> date | None:
        return self.__value

    @value.setter
    def value(self, new_value: date | None) -> None:
        self.__set_value(new_value)
        self.__emit_value()

    @property
    def error(self) -> ft.StrOrControl | None:
        return self.__text_field.error

    @error.setter
    def error(self, message: str | None) -> None:
        self.__text_field.error = message
        BaseComponent.safe_update(self.__text_field)

    def set_validation_height(self, height: int | float) -> None:
        self.height = height
        self.__text_field.height = height

    @property
    def read_only(self) -> bool:
        return self.__read_only

    @read_only.setter
    def read_only(self, new_value: bool) -> None:
        self.__read_only = new_value
        self.__open_button.disabled = self.__read_only
        self.__clear_button.disabled = self.__read_only or self.__value is None
        BaseComponent.safe_update(self.__open_button)
        BaseComponent.safe_update(self.__clear_button)

    def __emit_value(self) -> None:
        if not self.__on_change:
            return
        try:
            page = self.page
        except RuntimeError:
            return
        proxy = SimpleNamespace(
            target="",
            name="change",
            data=None,
            control=self.__text_field,
            page=page,
        )
        self.__on_change(cast(ft.ControlEvent, proxy))

    def __format_value(self, value: date | None) -> str:
        return value.strftime(self.__format) if value else ""

    def __normalize_input(self, value: date | datetime | None) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None

    def __set_value(self, new_value: date | None) -> None:
        self.__value = new_value
        self.__text_field.value = self.__format_value(self.__value)
        BaseComponent.safe_update(self.__text_field)
        if self.__picker.value != self.__value:
            self.__picker.value = self.__value
        self.__clear_button.disabled = self.__read_only or self.__value is None
        BaseComponent.safe_update(self.__clear_button)

    def __open_picker(self, _: ft.Event[ft.IconButton]) -> None:
        try:
            page = self.page
        except RuntimeError:
            return
        if not page:
            return
        self.__picker.open = True
        BaseComponent.safe_update(self.__picker)

    def __handle_picker_change(self, event: ft.Event[ft.DatePicker]) -> None:
        picked_raw_from_picker = getattr(self.__picker, "value", None)
        picked_raw_from_event = getattr(event, "data", None)
        picked = self.__normalize_event_data(picked_raw_from_event)
        if picked is None:
            picked = self.__normalize_input(picked_raw_from_picker)
        self.__set_value(picked)
        self.__emit_value()

    def __clear_date(self, _: ft.Event[ft.IconButton]) -> None:
        self.__set_value(None)
        self.__emit_value()

    @staticmethod
    def __normalize_event_data(raw_value: str | date | datetime | None) -> date | None:
        if raw_value is None:
            return None
        if isinstance(raw_value, datetime):
            if raw_value.tzinfo is not None and raw_value.utcoffset() == timedelta(0) and raw_value.hour >= 12:
                return (raw_value + timedelta(days=1)).date()
            return raw_value.date()
        if isinstance(raw_value, date):
            return raw_value
        raw_value_stripped = raw_value.strip()
        if len(raw_value_stripped) < 10:
            return None
        try:
            return date.fromisoformat(raw_value_stripped[:10])
        except ValueError:
            return None
