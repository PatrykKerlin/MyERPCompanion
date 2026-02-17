from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ControlStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.logistic.carrier_controller import CarrierController


class CarrierView(BaseView):
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
            {"key": "country", "input": self._get_text_input},
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
            {"key": "notes", "input": self._get_text_input, "lines": 3},
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
            height=AppDimensions.SECTION_HEIGHT_LARGE,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            on_add_clicked=self._controller.on_add_delivery_method_clicked,
            sort_by="id",
            with_border=True,
        )
        delivery_methods_section_height = (
            AppDimensions.SECTION_HEIGHT_LARGE + AppDimensions.CONTROL_HEIGHT + AppDimensions.SPACE_2XS
        )
        delivery_methods_label, _ = self._get_label("delivery_methods", 4)
        self.__delivery_methods_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                delivery_methods_label,
                ft.Container(
                    content=self.__delivery_methods_table,
                    col={"sm": 8.0},
                    alignment=ControlStyles.INPUT_ALIGNMENT,
                    height=delivery_methods_section_height,
                ),
            ],
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
        )

        columns = [
            ft.Column(
                controls=company_grid
                + street_grid
                + house_grid
                + city_grid
                + country_grid
                + contact_grid
                + self._spacing_responsive_row
                + [self.__delivery_methods_row],
                expand=True,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + bank_grid
                + notes_grid
                + [self._spacing_row, self._buttons_row],
                expand=True,
            ),
        ]

        self._columns_row.controls.extend(columns)
        self._master_column.controls.append(self._columns_row)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        is_read_mode = self._mode == ViewMode.READ
        is_delivery_methods_visible = self._is_details_mode()
        self.__delivery_methods_row.visible = is_delivery_methods_visible
        self.__delivery_methods_table.visible = is_delivery_methods_visible
        self.__delivery_methods_table.read_only = not is_read_mode
        self.__delivery_methods_row.update()
        self.__delivery_methods_table.update()
