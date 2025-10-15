from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.view_fields import FieldGroup
from views.base.base_view import BaseView
from views.controls.numeric_field_control import NumericField

if TYPE_CHECKING:
    from controllers.business.hr.employee_controller import EmployeeController
    from utils.translation import Translation


class EmployeeView(BaseView):
    def __init__(
        self,
        controller: EmployeeController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
        departments: list[tuple[int, str]],
        employees: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        personal_fields = {
            "first_name": FieldGroup(
                label=self._get_label("first_name", size=4),
                input=self._get_text_input("first_name", size=7),
                marker=self._get_marker("first_name", size=1),
            ),
            "middle_name": FieldGroup(
                label=self._get_label("middle_name", size=4),
                input=self._get_text_input("middle_name", size=7),
                marker=self._get_marker("middle_name", size=1),
            ),
            "last_name": FieldGroup(
                label=self._get_label("last_name", size=4),
                input=self._get_text_input("last_name", size=7),
                marker=self._get_marker("last_name", size=1),
            ),
            "pesel": FieldGroup(
                label=self._get_label("pesel", size=4),
                input=self._get_text_input("pesel", size=7),
                marker=self._get_marker("pesel", size=1),
            ),
            "birth_date": FieldGroup(
                label=self._get_label("birth_date", size=4),
                input=self._get_date_picker("birth_date", size=3),
                marker=self._get_marker("birth_date", size=5),
            ),
            "birth_place": FieldGroup(
                label=self._get_label("birth_place", size=4),
                input=self._get_text_input("birth_place", size=7),
                marker=self._get_marker("birth_place", size=1),
            ),
            "passport_number": FieldGroup(
                label=self._get_label("passport_number", size=4),
                input=self._get_text_input("passport_number", size=7),
                marker=self._get_marker("passport_number", size=1),
            ),
            "passport_expiry": FieldGroup(
                label=self._get_label("passport_expiry", size=4),
                input=self._get_date_picker("passport_expiry", size=3),
                marker=self._get_marker("passport_expiry", size=5),
            ),
            "id_card_number": FieldGroup(
                label=self._get_label("id_card_number", size=4),
                input=self._get_text_input("id_card_number", size=7),
                marker=self._get_marker("id_card_number", size=1),
            ),
            "id_card_expiry": FieldGroup(
                label=self._get_label("id_card_expiry", size=4),
                input=self._get_date_picker("id_card_expiry", size=3),
                marker=self._get_marker("id_card_expiry", size=5),
            ),
        }
        contact_fields = {
            "email": FieldGroup(
                label=self._get_label("email", size=4),
                input=self._get_text_input("email", size=7),
                marker=self._get_marker("email", size=1),
            ),
            "phone_number": FieldGroup(
                label=self._get_label("phone_number", size=4),
                input=self._get_text_input("phone_number", size=7),
                marker=self._get_marker("phone_number", size=1),
            ),
        }
        street_field = {
            "street": FieldGroup(
                label=self._get_label("street", size=4),
                input=self._get_text_input("street", size=7),
                marker=self._get_marker("street", size=1),
            ),
        }
        house_fields = {
            "house_number": FieldGroup(
                label=self._get_label("house_number", size=4),
                input=self._get_text_input("house_number", size=3),
                marker=self._get_marker("house_number", size=1),
            ),
            "apartment_number": FieldGroup(
                label=self._get_label("/", colon=False, size=1),
                input=self._get_text_input("apartment_number", size=2),
                marker=self._get_marker("apartment_number", size=1),
            ),
        }
        city_fields = {
            "city": FieldGroup(
                label=self._get_label("city", size=4),
                input=self._get_text_input("city", size=3),
                marker=self._get_marker("city", size=1),
            ),
            "postal_code": FieldGroup(
                label=self._get_label("postal_code", size=1),
                input=self._get_text_input("postal_code", size=2),
                marker=self._get_marker("postal_code", size=1),
            ),
        }
        country_field = {
            "country": FieldGroup(
                label=self._get_label("country", size=4),
                input=self._get_text_input("country", size=3),
                marker=self._get_marker("country", size=5),
            ),
        }
        employment_fields = {
            "hire_date": FieldGroup(
                label=self._get_label("hire_date", size=4),
                input=self._get_date_picker("hire_date", size=3),
                marker=self._get_marker("hire_date", size=5),
            ),
            "termination_date": FieldGroup(
                label=self._get_label("termination_date", size=4),
                input=self._get_date_picker("termination_date", size=3),
                marker=self._get_marker("termination_date", size=5),
            ),
            "manager_id": FieldGroup(
                label=self._get_label("manager", size=4),
                input=self._get_dropdown("manager_id", options=[], size=5),
                marker=self._get_marker("manager_id", 3),
            ),
            "department_id": FieldGroup(
                label=self._get_label("department", size=4),
                input=self._get_dropdown("department_id", options=[], size=5),
                marker=self._get_marker("department_id", 3),
            ),
            "position_id": FieldGroup(
                label=self._get_label("position", size=4),
                input=self._get_dropdown("position_id", options=[], size=5),
                marker=self._get_marker("position_id", 3),
            ),
            "salary": FieldGroup(
                label=self._get_label("salary", size=4),
                input=self._get_int_input("salary", 5),
                marker=self._get_marker("salary", 2),
            ),
        }
        bank_fields = {
            "bank_account": FieldGroup(
                label=self._get_label("bank_account", size=4),
                input=self._get_text_input("bank_account", size=7),
                marker=self._get_marker("bank_account", size=1),
            ),
            "bank_swift": FieldGroup(
                label=self._get_label("bank_swift", size=4),
                input=self._get_text_input("bank_swift", size=7),
                marker=self._get_marker("bank_swift", size=1),
            ),
            "bank_name": FieldGroup(
                label=self._get_label("bank_name", size=4),
                input=self._get_text_input("bank_name", size=7),
                marker=self._get_marker("bank_name", size=1),
            ),
        }

        self._inputs.update(personal_fields)
        self._inputs.update(contact_fields)
        self._inputs.update(street_field)
        self._inputs.update(house_fields)
        self._inputs.update(city_fields)
        self._inputs.update(country_field)
        self._inputs.update(employment_fields)
        self._inputs.update(bank_fields)

        self._inputs.update(self._meta_fields)
        personal_grid = self._build_grid(personal_fields)
        contact_grid = self._build_grid(contact_fields)
        street_grid = self._build_grid(street_field)
        house_grid = self._build_grid(house_fields, inline=True)
        city_grid = self._build_grid(city_fields, inline=True)
        country_grid = self._build_grid(country_field)
        employment_grid = self._build_grid(employment_fields)
        bank_grid = self._build_grid(bank_fields)

        meta_grid = self._build_grid(self._meta_fields)
        columns = [
            ft.Column(
                controls=personal_grid + contact_grid + street_grid + house_grid + city_grid + country_grid,
                expand=True,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid + (self._spacing_row * 2) + employment_grid + bank_grid,
                expand=True,
            ),
        ]
        rows = [
            ft.Row(
                controls=columns,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Row(height=25),
            ft.Row(
                controls=[self._search_button, self._cancel_button, self._save_button],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ]
        self._master_column.controls.extend(rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
