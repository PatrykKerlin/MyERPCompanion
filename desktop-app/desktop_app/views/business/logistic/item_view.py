from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.image_gallery_control import ImageGallery

if TYPE_CHECKING:
    from controllers.business.logistic.item_controller import ItemController


class ItemView(BaseView):
    def __init__(
        self,
        controller: ItemController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
        categories: list[tuple[int, str]],
        units: list[tuple[int, str]],
        suppliers: list[tuple[int, str]],
        currencies: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        product_fields_definitions = [
            {"key": "index", "input": self._get_text_input},
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "ean", "input": self._get_text_input},
            {"key": "category_id", "label": "category", "input": self._get_dropdown, "options": categories},
            {"key": "unit_id", "label": "unit", "input": self._get_dropdown, "options": units},
        ]
        financial_fields_definitions = [
            {"key": "supplier_id", "label": "supplier", "input": self._get_dropdown, "options": suppliers},
            {"key": "currency_id", "label": "currency", "input": self._get_dropdown, "options": currencies},
            {"key": "purchase_price", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "vat_rate", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "margin", "input": self._get_numeric_input, "is_float": True, "step": 0.001},
            {"key": "moq", "input": self._get_numeric_input},
        ]
        param_fields_definitions = [
            {"key": "is_available", "input": self._get_checkbox, "value": True},
            {"key": "is_fragile", "input": self._get_checkbox, "value": False},
            {"key": "is_package", "input": self._get_checkbox, "value": False},
            {"key": "is_returnable", "input": self._get_checkbox, "value": False},
        ]
        dimensions_fields_definitions = [
            {"key": "width", "input": self._get_numeric_input, "is_float": True, "step": 0.001},
            {"key": "height", "input": self._get_numeric_input, "is_float": True, "step": 0.001},
            {"key": "length", "input": self._get_numeric_input, "is_float": True, "step": 0.001},
            {"key": "weight", "input": self._get_numeric_input, "is_float": True, "step": 0.001},
            {"key": "expiration_date", "input": self._get_date_picker},
        ]
        stock_fields_definitions = [
            {"key": "stock_quantity", "input": self._get_numeric_input},
            {"key": "min_stock_level", "input": self._get_numeric_input},
            {"key": "max_stock_level", "input": self._get_numeric_input},
        ]

        product_fields = self._build_field_groups(product_fields_definitions)
        financial_fields = self._build_field_groups(financial_fields_definitions)
        param_fields = self._build_field_groups(param_fields_definitions)
        dimensions_fields = self._build_field_groups(dimensions_fields_definitions)
        stock_fields = self._build_field_groups(stock_fields_definitions)
        # images_field = {
        #     "images": FieldGroup(
        #         label=self._get_label("images", size=4),
        #         input=self._get_text_input("images", size=7),
        #         marker=self._get_marker("images", size=1),
        #     ),
        # }
        images: list[str] = []
        if data_row:
            for image in data_row.get("images") or []:
                url = image.get("url") if isinstance(image, dict) else getattr(image, "url", None)
                if url:
                    images.append(url)
        gallery = ImageGallery(image_urls=images, expand=True)

        self._add_to_inputs(product_fields, financial_fields, param_fields, dimensions_fields, stock_fields)
        main_grid = self._build_grid(product_fields)
        financial_grid = self._build_grid(financial_fields)
        param_grid = self._build_grid(param_fields)
        dimensions_grid = self._build_grid(dimensions_fields)
        stock_grid = self._build_grid(stock_fields)
        # images_grid = self._build_grid(images_field)
        meta_grid = self._get_meta_grid(label_size=4, id_size=2, datetime_size=7)
        columns = [
            ft.Column(
                controls=main_grid + financial_grid + dimensions_grid + stock_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid + self._spacing_responsive_row + [gallery] + param_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
