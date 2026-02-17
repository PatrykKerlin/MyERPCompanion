from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from styles.dimensions import AppDimensions
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.mixins.group_bulk_transfer_mixin import GroupBulkTransferMixin

if TYPE_CHECKING:
    from controllers.core.user_controller import UserController


class UserView(BaseView, GroupBulkTransferMixin):
    def __init__(
        self, # NOSONAR
        controller: UserController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
        themes: list[tuple[str, str]],
        employee_pairs: list[tuple[int, str]],
        customer_pairs: list[tuple[int, str]],
        warehouse_pairs: list[tuple[int, str]],
        show_username: bool,
        show_relations: bool,
        show_customer_relation: bool,
        show_employee_relation: bool,
        show_warehouses: bool,
        group_source_rows: list[tuple[int, list[str]]],
        group_target_rows: list[tuple[int, list[str]]],
        show_groups: bool,
        show_meta: bool = True,
        caller_view_key: View | None = None,
        on_groups_save_clicked=None,
        on_groups_delete_clicked=None,
    ) -> None:
        super().__init__(
            controller,
            translation,
            mode,
            key,
            data_row,
            4,
            7,
            caller_view_key=caller_view_key,
        )
        self.__password_validation_ready = False
        main_fields_definitions = [
            {"key": "password", "input": self._get_text_input, "password": True},
            {"key": "password_repeat", "input": self._get_text_input, "password": True},
            {"key": "language_id", "input": self._get_dropdown, "options": languages},
            {"key": "theme", "input": self._get_dropdown, "options": themes},
        ]
        if show_username:
            main_fields_definitions.insert(0, {"key": "username", "input": self._get_text_input})
        if show_warehouses:
            main_fields_definitions.append(
                {
                    "key": "warehouse_id",
                    "input": self._get_dropdown,
                    "options": warehouse_pairs,
                }
            )
        if show_relations and show_employee_relation:
            main_fields_definitions.append(
                {
                    "key": "employee_id",
                    "input": self._get_dropdown,
                    "options": employee_pairs,
                    "callbacks": [self.__handle_employee_changed],
                }
            )
        if show_relations and show_customer_relation:
            main_fields_definitions.append(
                {
                    "key": "customer_id",
                    "input": self._get_dropdown,
                    "options": customer_pairs,
                    "callbacks": [self.__handle_customer_changed],
                }
            )
        if data_row and isinstance(data_row.get("language"), dict):
            data_row["language_id"] = data_row["language"]["id"]
        self._search_disabled_fields.update({"password", "password_repeat"})
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        self.__hide_password_markers()
        if mode in {ViewMode.CREATE, ViewMode.EDIT}:
            self.__bind_password_validation()
        main_grid = self._build_grid(main_fields)
        columns: list[ft.Control] = [ft.Column(controls=main_grid, expand=True)]
        if show_meta:
            meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)
            columns = [
                ft.Column(controls=main_grid, expand=True),
                self._spacing_column,
                ft.Column(controls=meta_grid, expand=True),
            ]
        self._columns_row.controls = columns

        group_row = None
        if show_groups:
            self._init_group_bulk_transfer(
                mode=mode,
                source_rows=group_source_rows,
                target_rows=group_target_rows,
                source_label=self._translation.get("available_groups"),
                target_label=self._translation.get("user_groups"),
                on_save_clicked=on_groups_save_clicked,
                on_delete_clicked=on_groups_delete_clicked,
                height=AppDimensions.BULK_TRANSFER_HEIGHT_LARGE,
                visible_modes=set(self._DETAIL_MODES),
            )
            group_row = self._build_group_bulk_transfer_row()
        show_spacing = mode != ViewMode.READ
        self.__buttons_spacing_row = ft.Row(
            height=AppDimensions.SPACE_2XL,
            visible=show_spacing,
        )
        group_controls: list[ft.Control] = [self._spacing_row, group_row] if group_row is not None else []
        self._master_column.controls = [
            self._columns_row,
            self.__buttons_spacing_row,
            self._buttons_row,
            *group_controls,
        ]

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        show_spacing = mode != ViewMode.READ
        self.__buttons_spacing_row.visible = show_spacing
        self.safe_update(self.__buttons_spacing_row)
        if mode in {ViewMode.CREATE, ViewMode.EDIT} and self.__password_validation_ready:
            self.__validate_password_fields()

    def did_mount(self):
        self.__password_validation_ready = True
        if self._mode in {ViewMode.CREATE, ViewMode.EDIT}:
            self.__validate_password_fields()
        if hasattr(self, "_group_bulk_transfer"):
            self._mount_group_bulk_transfer()
        return super().did_mount()

    def __handle_employee_changed(self) -> None:
        field = self._inputs.get("employee_id")
        if not field:
            return
        control = field.input.content
        if not isinstance(control, ft.Dropdown):
            return
        if not control.value or control.value == "0":
            return
        self.__clear_other_selection("customer_id")

    def __handle_customer_changed(self) -> None:
        field = self._inputs.get("customer_id")
        if not field:
            return
        control = field.input.content
        if not isinstance(control, ft.Dropdown):
            return
        if not control.value or control.value == "0":
            return
        self.__clear_other_selection("employee_id")

    def __clear_other_selection(self, key: str) -> None:
        field = self._inputs.get(key)
        if not field:
            return
        control = field.input.content
        if isinstance(control, ft.Dropdown):
            control.value = "0"
            control.update()
        self._controller.set_field_value(key, None)

    def __hide_password_markers(self) -> None:
        for key in ("password", "password_repeat"):
            field = self._inputs.get(key)
            if not field or not field.marker:
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
        for key, field in (("password", password_field), ("password_repeat", repeat_field)):
            control = field.input.content
            if isinstance(control, ft.TextField):
                control.on_change = lambda event, key=key: (
                    self._controller.on_value_changed(event, key),
                    self.__validate_password_fields(),
                )
                control.on_blur = lambda _: self.__validate_password_fields()
        if self.__password_validation_ready:
            self.__validate_password_fields()
