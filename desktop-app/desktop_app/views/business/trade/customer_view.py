from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.mixins.discount_bulk_transfer_mixin import DiscountBulkTransferMixin
from views.mixins.user_link_view_mixin import UserLinkViewMixin

if TYPE_CHECKING:
    from controllers.business.trade.customer_controller import CustomerController


class CustomerView(BaseView, DiscountBulkTransferMixin, UserLinkViewMixin):
    def __init__(
        self,
        controller: CustomerController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        discount_source_items: list[tuple[int, str]],
        discount_target_items: list[tuple[int, str]],
        user_options: list[tuple[int, str]],
        on_discount_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_discount_delete_clicked: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)

        company_fields_definitions = [
            {"key": "first_name", "input": self._get_text_input},
            {"key": "last_name", "input": self._get_text_input},
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

        company_fields = self._build_field_groups(company_fields_definitions)
        financial_fields = self._build_field_groups(financial_fields_definitions)
        contact_fields = self._build_field_groups(contact_fields_definitions)
        street_field = self._build_field_groups(street_field_definition)
        house_fields = self._build_field_groups(house_fields_definitions)
        city_fields = self._build_field_groups(city_fields_definitions)
        country_field = self._build_field_groups(country_field_definition)
        shipping_street_field = self._build_field_groups(shipping_street_field_definition)
        shipping_house_fields = self._build_field_groups(shipping_house_fields_definitions)
        shipping_city_fields = self._build_field_groups(shipping_city_fields_definitions)
        shipping_country_field = self._build_field_groups(shipping_country_field_definition)

        user_field = self._init_user_link_field(user_options, self._controller.on_add_user_clicked, input_size=7)

        self._add_to_inputs(
            company_fields,
            financial_fields,
            contact_fields,
            street_field,
            house_fields,
            city_fields,
            country_field,
            shipping_street_field,
            shipping_house_fields,
            shipping_city_fields,
            shipping_country_field,
            user_field,
        )

        company_grid = self._build_grid(company_fields)
        financial_grid = self._build_grid(financial_fields)
        contact_grid = self._build_grid(contact_fields)
        street_grid = self._build_grid(street_field)
        house_grid = self._build_grid(house_fields, inline=True)
        city_grid = self._build_grid(city_fields, inline=True)
        country_grid = self._build_grid(country_field)
        shipping_street_grid = self._build_grid(shipping_street_field)
        shipping_house_grid = self._build_grid(shipping_house_fields, inline=True)
        shipping_city_grid = self._build_grid(shipping_city_fields, inline=True)
        shipping_country_grid = self._build_grid(shipping_country_field)
        user_grid = self._build_grid(user_field)

        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(
                controls=company_grid
                + financial_grid
                + contact_grid
                + street_grid
                + house_grid
                + city_grid
                + country_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + user_grid
                + self._spacing_responsive_row
                + shipping_street_grid
                + shipping_house_grid
                + shipping_city_grid
                + shipping_country_grid,
                expand=2,
            ),
        ]
        self._columns_row.controls.extend(columns)
        self._init_discount_bulk_transfer(
            mode,
            discount_source_items,
            discount_target_items,
            self._translation.get("discounts"),
            self._translation.get("customer_discounts"),
            on_discount_save_clicked,
            on_discount_delete_clicked,
            height=250,
            visible_modes={ViewMode.READ, ViewMode.EDIT},
        )
        bulk_transfer_row = self._build_discount_bulk_transfer_row()
        self._master_column.controls.extend(
            [
                self._columns_row,
                ft.Row(height=25),
                bulk_transfer_row,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )

    def clear_inputs(self) -> None:
        super().clear_inputs()
        self._reset_user_link()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self._update_discount_bulk_transfer_mode(mode)
        self._apply_user_link_mode(mode)

    def set_dropdown_options(self, key: str, options: list[tuple[int, str]]) -> None:
        if self._set_user_link_dropdown_options(key, options):
            return

    def did_mount(self):
        self._mount_discount_bulk_transfer()
        return super().did_mount()
