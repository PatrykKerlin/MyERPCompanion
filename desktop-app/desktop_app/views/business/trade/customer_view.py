from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from controllers.business.trade.customer_controller import CustomerController


class CustomerView(BaseView):
    def __init__(
        self,
        controller: CustomerController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        discount_source_items: list[tuple[int, str]],
        discount_target_items: list[tuple[int, str]],
        on_discount_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_discount_delete_clicked: Callable[[list[int]], None] | None = None,
        # users: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        # user_field_definition = [
        #     {"key": "user_id", "input": self._get_dropdown, "options": users},
        # ]
        personal_fields_definitions = [
            {"key": "first_name", "input": self._get_text_input},
            {"key": "middle_name", "input": self._get_text_input},
            {"key": "last_name", "input": self._get_text_input},
        ]

        company_fields_definitions = [
            {"key": "is_company", "input": self._get_checkbox},
            {"key": "company_name", "input": self._get_text_input},
        ]
        financial_fields_definitions = [
            {"key": "payment_term", "input": self._get_numeric_input},
            {"key": "tax_id", "input": self._get_text_input},
        ]
        contact_fields_definitions = [
            {"key": "email", "input": self._get_text_input},
            {"key": "phone_number", "input": self._get_text_input},
        ]
        address_field_definition = [
            {"key": "use_one_address", "input": self._get_checkbox},
        ]

        shipping_street_field_definition = [
            {"key": "shipping_street", "input": self._get_text_input},
        ]
        shipping_house_fields_definitions = [
            {"key": "shipping_house_number", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "shipping_apartment_number",
                "label": "/",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
                "colon": False,
            },
        ]
        shipping_city_fields_definitions = [
            {"key": "shipping_city", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "shipping_postal_code",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
            },
        ]
        shipping_country_field_definition = [
            {"key": "shipping_country", "input": self._get_text_input, "input_size": 3},
        ]
        billing_street_field_definition = [
            {"key": "billing_street", "input": self._get_text_input},
        ]
        billing_house_fields_definitions = [
            {"key": "billing_house_number", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "billing_apartment_number",
                "label": "/",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
                "colon": False,
            },
        ]
        billing_city_fields_definitions = [
            {"key": "billing_city", "input": self._get_text_input, "input_size": 3, "columns": 8},
            {
                "key": "billing_postal_code",
                "input": self._get_text_input,
                "label_size": 1,
                "input_size": 2,
                "columns": 4,
            },
        ]
        billing_country_field_definition = [
            {"key": "billing_country", "input": self._get_text_input, "input_size": 3},
        ]

        # user_field = self._build_field_groups(user_field_definition)
        personal_fields = self._build_field_groups(personal_fields_definitions)
        company_fields = self._build_field_groups(company_fields_definitions)
        financial_fields = self._build_field_groups(financial_fields_definitions)
        contact_fields = self._build_field_groups(contact_fields_definitions)
        address_field = self._build_field_groups(address_field_definition)
        shipping_street_field = self._build_field_groups(shipping_street_field_definition)
        shipping_house_fields = self._build_field_groups(shipping_house_fields_definitions)
        shipping_city_fields = self._build_field_groups(shipping_city_fields_definitions)
        shipping_country_field = self._build_field_groups(shipping_country_field_definition)
        billing_street_field = self._build_field_groups(billing_street_field_definition)
        billing_house_fields = self._build_field_groups(billing_house_fields_definitions)
        billing_city_fields = self._build_field_groups(billing_city_fields_definitions)
        billing_country_field = self._build_field_groups(billing_country_field_definition)

        self._add_to_inputs(
            # user_field,
            personal_fields,
            company_fields,
            financial_fields,
            contact_fields,
            address_field,
            shipping_street_field,
            shipping_house_fields,
            shipping_city_fields,
            shipping_country_field,
            billing_street_field,
            billing_house_fields,
            billing_city_fields,
            billing_country_field,
        )

        # user_grid = self._build_grid(user_field)
        personal_grid = self._build_grid(personal_fields)
        company_grid = self._build_grid(company_fields)
        financial_grid = self._build_grid(financial_fields)
        contact_grid = self._build_grid(contact_fields)
        address_grid = self._build_grid(address_field)
        shipping_street_grid = self._build_grid(shipping_street_field)
        shipping_house_grid = self._build_grid(shipping_house_fields, inline=True)
        shipping_city_grid = self._build_grid(shipping_city_fields, inline=True)
        shipping_country_grid = self._build_grid(shipping_country_field)
        billing_street_grid = self._build_grid(billing_street_field)
        billing_house_grid = self._build_grid(billing_house_fields, inline=True)
        billing_city_grid = self._build_grid(billing_city_fields, inline=True)
        billing_country_grid = self._build_grid(billing_country_field)

        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(
                controls=
                # user_grid
                personal_grid
                + company_grid
                + contact_grid
                + address_grid
                + shipping_street_grid
                + shipping_house_grid
                + shipping_city_grid
                + shipping_country_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + financial_grid
                + billing_street_grid
                + billing_house_grid
                + billing_city_grid
                + billing_country_grid,
                expand=2,
            ),
        ]
        self._columns_row.controls.extend(columns)
        self.__bulk_transfer = BulkTransfer(
            on_save_clicked=on_discount_save_clicked or (lambda _: None),
            source_label=self._translation.get("discounts"),
            target_label=self._translation.get("customer_discounts"),
            on_delete_clicked=on_discount_delete_clicked,
        )
        self.__pending_discount_source_items = discount_source_items
        self.__pending_discount_target_items = discount_target_items
        self.__bulk_transfer.visible = mode in {ViewMode.EDIT, ViewMode.READ}
        self.__set_bulk_transfer_state(mode)

        bulk_transfer_row = ft.Row(
            controls=[ft.Container(content=self.__bulk_transfer, expand=True, height=260)],
        )
        self._master_column.controls.extend(
            [
                self._columns_row,
                ft.Row(height=25),
                bulk_transfer_row,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )

    def did_mount(self):
        self.__bulk_transfer.set_source_items(self.__pending_discount_source_items)
        self.__bulk_transfer.set_target_items(self.__pending_discount_target_items)
        return super().did_mount()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self.__bulk_transfer.visible = mode in {ViewMode.CREATE, ViewMode.EDIT, ViewMode.READ}
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()

    def __set_bulk_transfer_state(self, mode: ViewMode) -> None:
        editable = mode == ViewMode.READ
        self.__bulk_transfer.set_enabled_states(editable, editable, editable)

    def get_pending_discount_ids(self) -> list[int]:
        return self.__bulk_transfer.get_pending_move_ids()

    def set_discount_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_source_items(items)

    def set_discount_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_target_items(items)
