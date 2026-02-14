from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from styles import AppDimensions
from utils.enums import View, ViewMode
from views.base.base_view import BaseView
from views.controls.data_table_control import DataTable
from views.mixins.user_link_view_mixin import UserLinkViewMixin

if TYPE_CHECKING:
    from controllers.business.hr.employee_controller import EmployeeController
    from utils.translation import Translation


class EmployeeView(BaseView, UserLinkViewMixin):
    def __init__(
        self,
        controller: EmployeeController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        departments: list[tuple[int, str]],
        positions: list[tuple[int, str]],
        managers: list[tuple[int, str]],
        user_options: list[tuple[int, str]],
        subordinate_rows: list[dict[str, Any]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        personal_fields_definitions = [
            {"key": "first_name", "input": self._get_text_input},
            {"key": "middle_name", "input": self._get_text_input},
            {"key": "last_name", "input": self._get_text_input},
            {"key": "pesel", "input": self._get_text_input},
            {"key": "birth_date", "input": self._get_date_picker, "input_size": 4},
            {"key": "birth_place", "input": self._get_text_input},
            {"key": "passport_number", "input": self._get_text_input},
            {"key": "passport_expiry", "input": self._get_date_picker, "input_size": 4},
            {"key": "id_card_number", "input": self._get_text_input},
            {"key": "id_card_expiry", "input": self._get_date_picker, "input_size": 4},
        ]
        contact_fields_definitions = [
            {"key": "email", "input": self._get_text_input},
            {"key": "phone_number", "input": self._get_text_input},
        ]
        street_field_definition = [
            {"key": "street", "input": self._get_text_input},
        ]
        house_fields_definitions = [
            {"key": "house_number", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "apartment_number",
                "label": "/",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
                "colon": False,
            },
        ]
        city_fields_definitions = [
            {"key": "city", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "postal_code",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
            },
        ]
        country_field_definition = [
            {"key": "country", "input": self._get_text_input, "input_size": 3},
        ]
        employment_fields_definitions = [
            {"key": "hire_date", "input": self._get_date_picker, "input_size": 5},
            {"key": "termination_date", "input": self._get_date_picker, "input_size": 5},
            {
                "key": "department_id",
                "input": self._get_dropdown,
                "input_size": 5,
                "options": departments,
                "callbacks": [self._controller.on_department_changed],
            },
            {
                "key": "position_id",
                "input": self._get_dropdown,
                "input_size": 5,
                "options": positions,
                "callbacks": [self._controller.on_position_changed],
            },
            {
                "key": "manager_id",
                "input": self._get_dropdown,
                "input_size": 5,
                "options": managers,
            },
            {
                "key": "is_remote",
                "input": self._get_radio_group,
                "input_size": 5,
                "options": [("false", "on_site"), ("true", "remote")],
                "default": "false",
            },
            {"key": "salary", "input": self._get_numeric_input, "input_size": 5},
        ]
        bank_fields_definitions = [
            {"key": "bank_account", "input": self._get_text_input},
            {"key": "bank_swift", "input": self._get_text_input},
            {"key": "bank_name", "input": self._get_text_input},
        ]

        personal_fields = self._build_field_groups(personal_fields_definitions)
        contact_fields = self._build_field_groups(contact_fields_definitions)
        street_field = self._build_field_groups(street_field_definition)
        house_fields = self._build_field_groups(house_fields_definitions)
        city_fields = self._build_field_groups(city_fields_definitions)
        country_field = self._build_field_groups(country_field_definition)
        employment_fields = self._build_field_groups(employment_fields_definitions)
        bank_fields = self._build_field_groups(bank_fields_definitions)

        user_field = self._init_user_link_field(user_options, self._controller.on_add_user_clicked, input_size=7)

        self._add_to_inputs(
            personal_fields,
            contact_fields,
            street_field,
            house_fields,
            city_fields,
            country_field,
            employment_fields,
            bank_fields,
            user_field,
        )

        personal_grid = self._build_grid(personal_fields)
        contact_grid = self._build_grid(contact_fields)
        street_grid = self._build_grid(street_field)
        house_grid = self._build_grid(house_fields, inline=True)
        city_grid = self._build_grid(city_fields, inline=True)
        country_grid = self._build_grid(country_field)
        user_grid = self._build_grid(user_field)
        self.__subordinates_table = DataTable(
            columns=["id", "first_name", "last_name"],
            rows=subordinate_rows,
            translation=self._translation,
            height=AppDimensions.SUBSECTION_HEIGHT,
            with_button=False,
        )
        employment_grid = self._build_grid(employment_fields)
        bank_grid = self._build_grid(bank_fields)

        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)
        columns = [
            ft.Column(
                controls=personal_grid + contact_grid + street_grid + house_grid + city_grid + country_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + employment_grid
                + bank_grid
                + user_grid
                + [self.__subordinates_table],
                expand=2,
            ),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def clear_inputs(self) -> None:
        super().clear_inputs()
        self._reset_user_link()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self._apply_user_link_mode(mode)
        if self._mode in {ViewMode.READ, ViewMode.EDIT}:
            self.__subordinates_table.visible = True
        else:
            self.__subordinates_table.visible = False
        self.__subordinates_table.read_only = True
        self.__subordinates_table.update()

    def set_dropdown_options(self, key: str, options: list[tuple[int, str]]) -> None:
        if self._set_user_link_dropdown_options(key, options):
            return
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
            dropdown.update()
