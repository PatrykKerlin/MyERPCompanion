from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.mixins.group_bulk_transfer_mixin import GroupBulkTransferMixin

if TYPE_CHECKING:
    from controllers.core.user_controller import UserController


class UserView(BaseView, GroupBulkTransferMixin):
    def __init__(
        self,
        controller: UserController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
        themes: list[tuple[str, str]],
        group_source_rows: list[tuple[int, list[str]]],
        group_target_rows: list[tuple[int, list[str]]],
        on_groups_save_clicked=None,
        on_groups_delete_clicked=None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        main_fields_definitions = [
            {"key": "username", "input": self._get_text_input},
            {"key": "password", "input": self._get_password_input},
            {"key": "password_repeat", "input": self._get_password_input},
            {"key": "language_id", "input": self._get_dropdown, "options": languages},
            {"key": "theme", "input": self._get_dropdown, "options": themes},
        ]
        self._search_disabled_fields.update({"password", "password_repeat"})
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        self.__hide_password_markers()
        if mode in {ViewMode.CREATE, ViewMode.EDIT}:
            self.__bind_password_validation()
        if mode == ViewMode.CREATE:
            self.__validate_password_fields()
            self.update()
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid, expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._init_group_bulk_transfer(
            mode=mode,
            source_rows=group_source_rows,
            target_rows=group_target_rows,
            source_label=self._translation.get("available_groups"),
            target_label=self._translation.get("user_groups"),
            on_save_clicked=on_groups_save_clicked,
            on_delete_clicked=on_groups_delete_clicked,
            height=260,
            visible_modes={ViewMode.READ, ViewMode.EDIT},
        )
        group_row = self._build_group_bulk_transfer_row()
        self._master_column.controls.extend([
            self._columns_row,
            ft.Row(height=25),
            group_row,
            ft.Row(height=25),
            self._buttons_row,
        ])

    def __hide_password_markers(self) -> None:
        for key in ("password", "password_repeat"):
            field = self._inputs.get(key)
            if not field:
                continue
            marker = field.marker.content
            if hasattr(marker, "visible"):
                setattr(marker, "visible", False)
            if hasattr(marker, "width"):
                setattr(marker, "width", 0)

    def __validate_password_fields(self) -> None:
        password_field = self._inputs.get("password")
        repeat_field = self._inputs.get("password_repeat")
        if not password_field or not repeat_field:
            return
        password_value = getattr(password_field.input.content, "value", "") if password_field.input else ""
        repeat_value = getattr(repeat_field.input.content, "value", "") if repeat_field.input else ""
        password_value = "" if password_value is None else str(password_value)
        repeat_value = "" if repeat_value is None else str(repeat_value)
        required_message = self._translation.get("value_required")
        mismatch_message = self._translation.get("passwords_do_not_match")
        if self._mode == ViewMode.CREATE:
            if not password_value:
                self.set_field_error("password", required_message)
            else:
                self.set_field_error("password", None)
            if not repeat_value:
                self.set_field_error("password_repeat", required_message)
            else:
                self.set_field_error("password_repeat", None)
            if password_value and repeat_value and password_value != repeat_value:
                self.set_field_error("password", mismatch_message)
                self.set_field_error("password_repeat", mismatch_message)
            return
        # EDIT mode: optional change, but if one is set, both must match
        if not password_value and not repeat_value:
            self.set_field_error("password", None)
            self.set_field_error("password_repeat", None)
            return
        if not password_value:
            self.set_field_error("password", required_message)
            return
        if not repeat_value:
            self.set_field_error("password_repeat", required_message)
            return
        if password_value != repeat_value:
            self.set_field_error("password", mismatch_message)
            self.set_field_error("password_repeat", mismatch_message)
        else:
            self.set_field_error("password", None)
            self.set_field_error("password_repeat", None)

    def __bind_password_validation(self) -> None:
        password_field = self._inputs.get("password")
        repeat_field = self._inputs.get("password_repeat")
        if not password_field or not repeat_field:
            return
        for field in (password_field, repeat_field):
            control = field.input.content
            if hasattr(control, "on_change"):
                control.on_change = lambda event, key=field.key: (self._controller.on_value_changed(event, key), self.__validate_password_fields())
            if hasattr(control, "on_blur"):
                control.on_blur = lambda _: self.__validate_password_fields()
        self.__validate_password_fields()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode in {ViewMode.CREATE, ViewMode.EDIT}:
            self.__validate_password_fields()

    def did_mount(self):
        self._mount_group_bulk_transfer()
        return super().did_mount()
