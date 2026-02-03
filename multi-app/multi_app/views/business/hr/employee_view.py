from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import flet as ft

from utils.enums import View, ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.hr.employee_controller import EmployeeController
    from utils.translation import Translation


class EmployeeView(BaseView):
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

        dropdown_container, input_size = self._get_dropdown("user_id", 7, user_options)
        dropdown = dropdown_container.content
        self.__user_dropdown = dropdown if isinstance(dropdown, ft.Dropdown) else None
        self.__user_dropdown_options: list[ft.DropdownOption] | None = None
        self.__user_button = ft.IconButton(
            icon=ft.Icons.PERSON_ADD,
            on_click=self._controller.on_add_user_clicked,
        )
        user_input = ft.Container(
            content=ft.Row(
                controls=[cast(ft.Control, dropdown), self.__user_button],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=8,
            ),
            col={"sm": float(input_size)},
            alignment=self._base_alignment,
        )
        user_field = {
            "user_id": FieldGroup(
                label=self._get_label("user_id", 4),
                input=(user_input, input_size),
                marker=self._get_marker("user_id", 1),
            )
        }

        user_id_value = data_row.get("user_id") if data_row else None
        if self.__user_dropdown and user_id_value is not None:
            match = None
            for option in self.__user_dropdown.options:
                if option.key == str(user_id_value):
                    match = option
                    break
            if match is None:
                self.__user_dropdown.options.append(ft.dropdown.Option(key=str(user_id_value), text=str(user_id_value)))
            self.__user_dropdown.value = str(user_id_value)
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
                controls=meta_grid + self._spacing_responsive_row + employment_grid + bank_grid + user_grid,
                expand=2,
            ),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def clear_inputs(self) -> None:
        super().clear_inputs()
        if self.__user_dropdown:
            self.__user_dropdown.value = "0"
            self.__user_dropdown.update()


    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        field = self._inputs.get("user_id")
        row = field.input.content if field else None
        dropdown = self.__user_dropdown
        marker_value = False
        if field and field.marker and hasattr(field.marker.content, "value"):
            marker_value = bool(field.marker.content.value)
        user_id_value = self._data_row.get("user_id") if self._data_row else None
        if user_id_value in (0, "0", ""):
            user_id_value = None
        if dropdown:
            if mode == ViewMode.READ:
                if user_id_value is not None:
                    if self.__user_dropdown_options is None:
                        self.__user_dropdown_options = list(dropdown.options)
                    matching = [option for option in dropdown.options if option.key == str(user_id_value)]
                    if matching:
                        dropdown.options = matching
                        dropdown.value = matching[0].key
                else:
                    if self.__user_dropdown_options is not None:
                        dropdown.options = self.__user_dropdown_options
                        self.__user_dropdown_options = None
                    dropdown.value = "0"
            else:
                if self.__user_dropdown_options is not None:
                    dropdown.options = self.__user_dropdown_options
                    self.__user_dropdown_options = None
            if mode == ViewMode.SEARCH:
                dropdown.disabled = not marker_value
            elif mode in {ViewMode.CREATE, ViewMode.EDIT}:
                dropdown.disabled = True
            elif mode == ViewMode.READ:
                dropdown.disabled = False
            dropdown.update()
        if mode == ViewMode.READ:
            self.__user_button.disabled = user_id_value is not None
        else:
            self.__user_button.disabled = True
        if self.__user_button.page:
            self.__user_button.update()
        # keep row enabled in READ/SEARCH so dropdown/button can reflect their own state
        if hasattr(row, "disabled"):
            if mode in {ViewMode.CREATE, ViewMode.EDIT}:
                row.disabled = True
            else:
                row.disabled = False
            if row and row.page:
                row.update()






    def set_dropdown_options(self, key: str, options: list[tuple[int, str]]) -> None:
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
