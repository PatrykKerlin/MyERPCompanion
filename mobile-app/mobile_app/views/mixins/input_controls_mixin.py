from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any

import flet as ft
from styles.styles import ButtonStyles, ControlStyles
from views.controls.date_field_control import DateField
from views.controls.numeric_field_control import NumericField


class InputControlsMixin:
    @staticmethod
    def _get_label(
        value: str,
        style: ft.TextStyle | None = None,
        text_align: ft.TextAlign | None = None,
        selectable: bool | None = None,
        color: ft.ColorValue | None = None,
        no_wrap: bool | None = None,
        size: float | int | None = None,
    ) -> ft.Text:
        label = ft.Text(value=value, style=style, color=color, no_wrap=no_wrap, size=size)
        if text_align is not None:
            label.text_align = text_align
        if selectable is not None:
            label.selectable = selectable
        return label

    @staticmethod
    def _get_text_field(
        value: str = "",  # NOSONAR
        label: str | None = None,
        password: bool = False,
        can_reveal_password: bool | None = None,
        autofocus: bool = False,
        expand: bool | None = None,
        width: float | int | None = None,
        min_lines: int | None = None,
        max_lines: int | None = None,
        on_change: Callable[[ft.Event[ft.TextField]], object] | None = None,
        on_submit: Callable[[ft.Event[ft.TextField]], object] | None = None,
        on_focus: Callable[[ft.Event[ft.TextField]], object] | None = None,
        on_blur: Callable[[ft.Event[ft.TextField]], object] | None = None,
        on_tap_outside: Callable[[ft.Event[ft.TextField]], object] | None = None,
        auto_submit_on_tap_outside: bool = True,
    ) -> ft.TextField:
        resolved_on_tap_outside = on_tap_outside
        if auto_submit_on_tap_outside and not password and resolved_on_tap_outside is None:
            resolved_on_tap_outside = on_submit or on_change
        return ft.TextField(
            value=value,
            label=label,
            password=password,
            can_reveal_password=password if can_reveal_password is None else can_reveal_password,
            autofocus=autofocus,
            expand=expand,
            width=width,
            min_lines=min_lines,
            max_lines=max_lines,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            on_change=on_change,
            on_submit=on_submit,
            on_focus=on_focus,
            on_blur=on_blur,
            on_tap_outside=resolved_on_tap_outside,
        )

    @staticmethod
    def _get_dropdown(
        options: Sequence[tuple[int | str, str]] | None = None,
        label: str | None = None,
        value: str | None = None,
        include_empty_option: bool = False,
        editable: bool = True,
        enable_search: bool = True,
        enable_filter: bool = True,
        disabled: bool = False,
        expand: bool | None = None,
        width: float | int | None = None,
        on_select: Callable[[ft.Event[ft.Dropdown]], object] | None = None,
    ) -> ft.Dropdown:
        resolved_options: list[ft.dropdown.Option] = []
        if include_empty_option:
            resolved_options.append(ft.dropdown.Option(key="0", text=""))
        for option_key, option_label in options or []:
            resolved_options.append(ft.dropdown.Option(key=str(option_key), text=option_label))
        return ft.Dropdown(
            label=label,
            options=resolved_options,
            value=value,
            editable=editable,
            enable_search=enable_search,
            enable_filter=enable_filter,
            disabled=disabled,
            expand=expand,
            width=width,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            on_select=on_select,
        )

    @staticmethod
    def _get_numeric_field(
        value: int | float = 0,
        step: int | float = 1,
        precision: int = 2,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        is_float: bool = False,
        expand: int | bool | None = None,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> NumericField:
        return NumericField(
            value=value,
            step=step,
            precision=precision,
            min_value=min_value,
            max_value=max_value,
            is_float=is_float,
            expand=expand,
            read_only=read_only,
            on_change=on_change,
        )

    @staticmethod
    def _get_date_field(
        value: date | datetime | None = None,
        min_date: date | datetime | None = None,
        max_date: date | datetime | None = None,
        date_format: str = "%Y-%m-%d",
        width: float | None = None,
        expand: int | bool | None = None,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> DateField:
        return DateField(
            value=value,
            min_date=min_date,
            max_date=max_date,
            date_format=date_format,
            width=width,
            expand=expand,
            read_only=read_only,
            on_change=on_change,
        )

    @staticmethod
    def _get_button(
        content: str | None = None,
        on_click: Callable[[ft.Event[ft.Button]], object] | None = None,
        width: float | int | None = None,
        disabled: bool = False,
        style: ft.ButtonStyle | None = None,
        icon: Any | None = None,
        tooltip: str | None = None,
    ) -> ft.Button:
        resolved_content = content
        if icon is not None and resolved_content is None:
            resolved_content = ""
        resolved_style = style or ButtonStyles.regular
        return ft.Button(
            content=resolved_content,
            on_click=on_click,
            width=width,
            disabled=disabled,
            style=resolved_style,
            icon=icon,
            tooltip=tooltip,
        )

    @staticmethod
    def _get_icon_button(
        icon: Any,
        on_click: Callable[[ft.Event[ft.IconButton]], object] | None = None,
        width: float | int | None = None,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> ft.IconButton:
        return ft.IconButton(
            icon=icon,
            on_click=on_click,
            width=width,
            disabled=disabled,
            tooltip=tooltip,
        )
