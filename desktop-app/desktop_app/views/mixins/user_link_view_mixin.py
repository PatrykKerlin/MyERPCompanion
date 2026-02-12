from __future__ import annotations

from typing import Any, Callable, cast

import flet as ft
from utils.enums import ViewMode
from utils.field_group import FieldGroup


class UserLinkViewMixin:
    _base_alignment: ft.Alignment
    _data_row: dict[str, Any] | None
    _inputs: dict[str, FieldGroup]
    _mode: ViewMode

    def _get_dropdown(
        self,
        key: str,
        size: int,
        options: list[tuple[int, str]],
        callbacks: list[Callable[..., None]] | None = None,
        label: str | None = None,
        value: int | str | None = "0",
    ) -> tuple[ft.Container, int]: ...
    def _get_label(self, key: str, size: int) -> tuple[ft.Container, int]: ...
    def _get_marker(self, key: str, size: int) -> tuple[ft.Container, int]: ...

    def _init_user_link_field(
        self,
        user_options: list[tuple[int, str]],
        on_add_user_clicked,
        input_size: int = 7,
        label_size: int = 4,
    ) -> dict[str, FieldGroup]:
        dropdown_container, size = self._get_dropdown("user_id", input_size, user_options)
        dropdown = dropdown_container.content
        self._user_dropdown = dropdown if isinstance(dropdown, ft.Dropdown) else None
        self._user_dropdown_options: list[ft.DropdownOption] | None = None
        self._user_button = ft.IconButton(
            icon=ft.Icons.PERSON_ADD,
            on_click=on_add_user_clicked,
        )
        user_input = ft.Container(
            content=ft.Row(
                controls=[cast(ft.Control, dropdown), self._user_button],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=8,
            ),
            col={"sm": float(size)},
            alignment=self._base_alignment,
        )
        user_field = {
            "user_id": FieldGroup(
                label=self._get_label("user_id", label_size),
                input=(user_input, size),
                marker=self._get_marker("user_id", 1),
            )
        }
        user_id_value = self._data_row.get("user_id") if self._data_row else None
        if self._user_dropdown and user_id_value is not None:
            match = None
            for option in self._user_dropdown.options:
                if option.key == str(user_id_value):
                    match = option
                    break
            if match is None:
                self._user_dropdown.options.append(ft.dropdown.Option(key=str(user_id_value), text=str(user_id_value)))
            self._user_dropdown.value = str(user_id_value)
        return user_field

    def _reset_user_link(self) -> None:
        dropdown = getattr(self, "_user_dropdown", None)
        if dropdown is not None:
            dropdown.value = "0"
            dropdown.update()

    def _apply_user_link_mode(self, mode: ViewMode) -> None:
        field = self._inputs.get("user_id")
        row = field.input.content if field else None
        dropdown = getattr(self, "_user_dropdown", None)
        marker_value = False
        if field and field.marker:
            marker = field.marker.content
            if isinstance(marker, ft.Checkbox):
                marker_value = bool(marker.value)
        user_id_value = self._data_row.get("user_id") if self._data_row else None
        if user_id_value in (0, "0", ""):
            user_id_value = None
        if dropdown:
            if mode == ViewMode.READ:
                if user_id_value is not None:
                    if self._user_dropdown_options is None:
                        self._user_dropdown_options = list(dropdown.options)
                    matching = [option for option in dropdown.options if option.key == str(user_id_value)]
                    if matching:
                        dropdown.options = matching
                        dropdown.value = matching[0].key
                else:
                    if self._user_dropdown_options is None:
                        self._user_dropdown_options = list(dropdown.options)
                    dropdown.options = []
                    dropdown.value = "0"
            else:
                if self._user_dropdown_options is not None:
                    dropdown.options = self._user_dropdown_options
                    self._user_dropdown_options = None
            if mode == ViewMode.SEARCH:
                dropdown.disabled = not marker_value
            elif mode in {ViewMode.CREATE, ViewMode.EDIT}:
                dropdown.disabled = True
            elif mode == ViewMode.READ:
                dropdown.disabled = False
            dropdown.update()
        if getattr(self, "_user_button", None):
            if mode == ViewMode.READ:
                self._user_button.disabled = user_id_value is not None
            else:
                self._user_button.disabled = True
            if self._user_button.page:
                self._user_button.update()
        if row is not None and hasattr(row, "disabled"):
            setattr(row, "disabled", mode in {ViewMode.CREATE, ViewMode.EDIT})
            if getattr(row, "page", None):
                row.update()

    def _set_user_link_dropdown_options(self, key: str, options: list[tuple[int, str]]) -> bool:
        if key != "user_id":
            return False
        field = self._inputs[key]
        control = field.input.content
        dropdown: ft.Dropdown | None = None
        if isinstance(control, ft.Dropdown):
            dropdown = control
        elif isinstance(control, ft.Row):
            for item in control.controls:
                if isinstance(item, ft.Dropdown):
                    dropdown = item
                    break
        if dropdown is not None:
            dropdown.options = [ft.dropdown.Option(text=label, key=str(value)) for value, label in options]
            if (
                key == "user_id"
                and self._mode == ViewMode.READ
                and self._data_row
                and self._data_row.get("user_id") is not None
            ):
                value = self._data_row.get("user_id")
                matching = [option for option in dropdown.options if option.key == str(value)]
                if matching:
                    dropdown.options = matching
                    dropdown.value = matching[0].key
            dropdown.update()
        return True
