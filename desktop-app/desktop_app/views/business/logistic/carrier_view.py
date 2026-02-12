from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_desktop_view import BaseDesktopView
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.logistic.carrier_controller import CarrierController


class CarrierView(BaseDesktopView):
    def __init__(
        self,
        controller: CarrierController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
        delivery_methods: list[dict[str, Any]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        company_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "company_email", "input": self._get_text_input},
            {"key": "company_phone", "input": self._get_text_input},
            {"key": "company_website", "input": self._get_text_input},
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
        contact_fields_definitions = [
            {"key": "contact_person", "input": self._get_text_input},
            {"key": "contact_phone", "input": self._get_text_input},
            {"key": "contact_email", "input": self._get_text_input},
        ]
        bank_fields_definitions = [
            {"key": "bank_account", "input": self._get_text_input},
            {"key": "bank_swift", "input": self._get_text_input},
            {"key": "bank_name", "input": self._get_text_input},
            {"key": "tax_id", "input": self._get_text_input},
            {"key": "payment_term", "input": self._get_numeric_input},
            {"key": "currency_id", "input": self._get_dropdown, "options": currencies},
        ]
        notes_field_definition = [
            {"key": "notes", "input": self._get_text_input, "lines": 5},
        ]

        company_fields = self._build_field_groups(company_fields_definitions)
        street_field = self._build_field_groups(street_field_definition)
        house_fields = self._build_field_groups(house_fields_definitions)
        city_fields = self._build_field_groups(city_fields_definitions)
        country_field = self._build_field_groups(country_field_definition)
        contact_fields = self._build_field_groups(contact_fields_definitions)
        bank_fields = self._build_field_groups(bank_fields_definitions)
        notes_field = self._build_field_groups(notes_field_definition)

        self._add_to_inputs(
            company_fields,
            street_field,
            house_fields,
            city_fields,
            country_field,
            contact_fields,
            bank_fields,
            notes_field,
        )

        company_grid = self._build_grid(company_fields)
        street_grid = self._build_grid(street_field)
        house_grid = self._build_grid(house_fields, inline=True)
        city_grid = self._build_grid(city_fields, inline=True)
        country_grid = self._build_grid(country_field)
        contact_grid = self._build_grid(contact_fields)
        bank_grid = self._build_grid(bank_fields)
        notes_grid = self._build_grid(notes_field)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        self.__delivery_methods_table = DataTable(
            columns=["id", "name", "description", "price_per_unit", "unit_id"],
            rows=delivery_methods,
            translation=self._translation,
            height=250,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            on_add_clicked=self._controller.on_add_delivery_method_clicked,
            sort_by="id",
        )

        columns = [
            ft.Column(
                controls=company_grid
                + street_grid
                + house_grid
                + city_grid
                + country_grid
                + contact_grid
                + [self.__delivery_methods_table],
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid + self._spacing_responsive_row + bank_grid + notes_grid, expand=2),
        ]

        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if self._mode not in {ViewMode.READ, ViewMode.EDIT}:
            self.__delivery_methods_table.add_button.disabled = True
            self.__delivery_methods_table.visible = False
        elif self._mode == ViewMode.EDIT:
            self.__delivery_methods_table.visible = True
            self.__delivery_methods_table.read_only = True
        elif self._mode == ViewMode.READ:
            self.__delivery_methods_table.read_only = False
            self.__delivery_methods_table.add_button.disabled = False
            self.__delivery_methods_table.add_button.visible = True
        self.__delivery_methods_table.update()
