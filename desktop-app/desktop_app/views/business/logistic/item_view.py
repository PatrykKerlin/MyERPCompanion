from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
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
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        main_fields = {
            "index": FieldGroup(
                label=self._get_label("index", size=4),
                input=self._get_text_input("index", size=7),
                marker=self._get_marker("index", size=1),
            ),
            "name": FieldGroup(
                label=self._get_label("name", size=4),
                input=self._get_text_input("name", size=7),
                marker=self._get_marker("name", size=1),
            ),
            "description": FieldGroup(
                label=self._get_label("description", size=4),
                input=self._get_text_input("description", lines=3, size=7),
                marker=self._get_marker("description", size=1),
            ),
            "ean": FieldGroup(
                label=self._get_label("ean", size=4),
                input=self._get_text_input("ean", size=7),
                marker=self._get_marker("ean", size=1),
            ),
            "category_id": FieldGroup(
                label=self._get_label("category", size=4),
                input=self._get_dropdown("category_id", options=[], size=7),
                marker=self._get_marker("category_id", size=1),
            ),
            "unit_id": FieldGroup(
                label=self._get_label("unit", size=4),
                input=self._get_dropdown("category_id", options=[], size=7),
                marker=self._get_marker("unit_id", size=1),
            ),
        }
        financial_fields = {
            "supplier_id": FieldGroup(
                label=self._get_label("supplier", size=4),
                input=self._get_dropdown("category_id", options=[], size=7),
                marker=self._get_marker("supplier_id", size=1),
            ),
            "purchase_price": FieldGroup(
                label=self._get_label("purchase_price", size=4),
                input=self._get_numeric_input("purchase_price", is_float=True, size=7),
                marker=self._get_marker("purchase_price", size=1),
            ),
            "currency_id": FieldGroup(
                label=self._get_label("currency", size=4),
                input=self._get_dropdown("category_id", options=[], size=7),
                marker=self._get_marker("currency_id", size=1),
            ),
            "moq": FieldGroup(
                label=self._get_label("moq", size=4),
                input=self._get_text_input("moq", size=7),
                marker=self._get_marker("moq", size=1),
            ),
            "vat_rate": FieldGroup(
                label=self._get_label("vat_rate", size=4),
                input=self._get_numeric_input("vat_rate", is_float=True, size=7),
                marker=self._get_marker("vat_rate", size=1),
            ),
            "margin": FieldGroup(
                label=self._get_label("margin", size=4),
                input=self._get_numeric_input("vat_rate", is_float=True, precision=3, size=7),
                marker=self._get_marker("margin", size=1),
            ),
        }
        param_fields = {
            "is_available": FieldGroup(
                label=self._get_label("is_available", size=4),
                input=self._get_checkbox("is_available", value=True, size=7),
                marker=self._get_marker("is_available", size=1),
            ),
            "is_fragile": FieldGroup(
                label=self._get_label("is_fragile", size=4),
                input=self._get_checkbox("is_available", value=False, size=7),
                marker=self._get_marker("is_fragile", size=1),
            ),
            "is_package": FieldGroup(
                label=self._get_label("is_package", size=4),
                input=self._get_checkbox("is_available", value=False, size=7),
                marker=self._get_marker("is_package", size=1),
            ),
            "is_returnable": FieldGroup(
                label=self._get_label("is_returnable", size=4),
                input=self._get_checkbox("is_available", value=False, size=7),
                marker=self._get_marker("is_returnable", size=1),
            ),
        }
        dimensions_fields = {
            "width": FieldGroup(
                label=self._get_label("width", size=4),
                input=self._get_numeric_input("width", is_float=True, precision=3, size=7),
                marker=self._get_marker("width", size=1),
            ),
            "height": FieldGroup(
                label=self._get_label("height", size=4),
                input=self._get_numeric_input("height", is_float=True, precision=3, size=7),
                marker=self._get_marker("height", size=1),
            ),
            "length": FieldGroup(
                label=self._get_label("length", size=4),
                input=self._get_numeric_input("length", is_float=True, precision=3, size=7),
                marker=self._get_marker("length", size=1),
            ),
            "weight": FieldGroup(
                label=self._get_label("weight", size=4),
                input=self._get_numeric_input("weight", is_float=True, precision=3, size=7),
                marker=self._get_marker("weight", size=1),
            ),
            "expiration_date": FieldGroup(
                label=self._get_label("expiration_date", size=4),
                input=self._get_date_picker("expiration_date", size=7),
                marker=self._get_marker("expiration_date", size=1),
            ),
        }
        stock_fields = {
            "stock_quantity": FieldGroup(
                label=self._get_label("stock_quantity", size=4),
                input=self._get_numeric_input("stock_quantity", size=7),
                marker=self._get_marker("stock_quantity", size=1),
            ),
            "min_stock_level": FieldGroup(
                label=self._get_label("min_stock_level", size=4),
                input=self._get_numeric_input("min_stock_level", size=7),
                marker=self._get_marker("min_stock_level", size=1),
            ),
            "max_stock_level": FieldGroup(
                label=self._get_label("max_stock_level", size=4),
                input=self._get_numeric_input("max_stock_level", size=7),
                marker=self._get_marker("max_stock_level", size=1),
            ),
        }
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

        self._add_to_inputs(main_fields, financial_fields, param_fields, dimensions_fields, stock_fields)
        main_grid = self._build_grid(main_fields)
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
