from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView
from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.business.logistic.warehouse_controller import WarehouseController


class WarehouseView(BaseView):
    def __init__(
        self,
        controller: WarehouseController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        main_fields = {
            "name": FieldGroup(
                label=self._get_label("name", size=4),
                input=self._get_text_input("name", size=7),
                marker=self._get_marker("name", size=1),
            ),
            "email": FieldGroup(
                label=self._get_label("email", size=4),
                input=self._get_text_input("email", size=7),
                marker=self._get_marker("email", size=1),
            ),
            "phone_number": FieldGroup(
                label=self._get_label("phone", size=4),
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
        self._add_to_inputs(main_fields, street_field, house_fields, city_fields, country_field)
        main_grid = self._build_grid(main_fields)
        street_grid = self._build_grid(street_field)
        house_grid = self._build_grid(house_fields, inline=True)
        city_grid = self._build_grid(city_fields, inline=True)
        country_grid = self._build_grid(country_field)
        meta_grid = self._get_meta_grid(label_size=4, id_size=2, datetime_size=7)
        columns = [
            ft.Column(
                controls=main_grid + street_grid + house_grid + city_grid + country_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
