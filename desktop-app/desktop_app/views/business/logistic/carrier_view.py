from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.table_control import TableControl

if TYPE_CHECKING:
    from controllers.business.logistic.carrier_controller import CarrierController


class CarrierView(BaseView):
    def __init__(
        self,
        controller: CarrierController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
        delivery_methods: list[dict[str, Any]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        company_fields = {
            "name": FieldGroup(
                label=self._get_label("name", size=4),
                input=self._get_text_input("name", size=7),
                marker=self._get_marker("name", size=1),
            ),
            "company_email": FieldGroup(
                label=self._get_label("company_email", size=4),
                input=self._get_text_input("company_email", size=7),
                marker=self._get_marker("company_email", size=1),
            ),
            "company_phone": FieldGroup(
                label=self._get_label("company_phone", size=4),
                input=self._get_text_input("company_phone", size=7),
                marker=self._get_marker("company_phone", size=1),
            ),
            "company_website": FieldGroup(
                label=self._get_label("company_website", size=4),
                input=self._get_text_input("company_website", size=7),
                marker=self._get_marker("company_website", size=1),
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
        contact_fields = {
            "contact_person": FieldGroup(
                label=self._get_label("contact_person", size=4),
                input=self._get_text_input("contact_person", size=7),
                marker=self._get_marker("contact_person", size=1),
            ),
            "contact_phone": FieldGroup(
                label=self._get_label("contact_phone", size=4),
                input=self._get_text_input("contact_phone", size=7),
                marker=self._get_marker("contact_phone", size=1),
            ),
            "contact_email": FieldGroup(
                label=self._get_label("contact_email", size=4),
                input=self._get_text_input("contact_email", size=7),
                marker=self._get_marker("contact_email", size=1),
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
            "tax_id": FieldGroup(
                label=self._get_label("tax_id", size=4),
                input=self._get_text_input("tax_id", size=7),
                marker=self._get_marker("tax_id", size=1),
            ),
            "payment_term": FieldGroup(
                label=self._get_label("payment_term", size=4),
                input=self._get_text_input("payment_term", size=7),
                marker=self._get_marker("payment_term", size=1),
            ),
            "currency_id": FieldGroup(
                label=self._get_label("currency", size=4),
                input=self._get_dropdown("currency_id", options=currencies, size=7),
                marker=self._get_marker("currency_id", size=1),
            ),
        }
        notes_field = {
            "notes": FieldGroup(
                label=self._get_label("notes", size=4),
                input=self._get_text_input("notes", lines=5, size=7),
                marker=self._get_marker("notes", size=1),
            ),
        }
        self.__table = TableControl(
            translation=self._translation,
            columns=["name", "price_per_unit", "max_width", "max_height", "max_length", "max_weight", "unit_id"],
            data=delivery_methods,
            sort_by=self._controller.search_params.sort_by,
            order=self._controller.search_params.order,
            on_sort_clicked=self._controller.on_sort_clicked,
            # on_row_clicked=lambda row_id: self._controller.on_row_clicked(row_id),
        )

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
        meta_grid = self._get_meta_grid(label_size=4, id_size=2, datetime_size=7)
        columns = [
            ft.Column(
                controls=company_grid
                + street_grid
                + house_grid
                + city_grid
                + country_grid
                + contact_grid
                + [self.__table],
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid + bank_grid + notes_grid, expand=2),
        ]
        table_column = [
            ft.Column(
                controls=[self.__table],
                expand=True,
            ),
        ]
        self._columns_row.controls.extend(columns)
        # self._columns_row.controls.extend(table_column)
        self._master_column.controls.extend(self._rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)

    # def set_mode(self, mode: ViewMode) -> None:
    #     super().set_mode(mode)
    #     if mode in {ViewMode.SEARCH}
    #     match mode:
    #         case ViewMode.SEARCH:
    #             self.__set_search_mode()
    #         case ViewMode.LIST:
    #             self.__set_list_mode()
    #         case ViewMode.READ:
    #             self.__set_read_mode()
    #         case ViewMode.CREATE:
    #             self.__set_create_mode()
    #         case ViewMode.EDIT:
    #             self.__set_edit_mode()
