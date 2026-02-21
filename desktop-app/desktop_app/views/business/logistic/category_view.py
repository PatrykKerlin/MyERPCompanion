from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from styles.dimensions import AppDimensions
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.mixins.discount_bulk_transfer_mixin import DiscountBulkTransferMixin, DiscountTransferItem

if TYPE_CHECKING:
    from controllers.business.logistic.category_controller import CategoryController


class CategoryView(BaseView, DiscountBulkTransferMixin):
    def __init__(
        self,
        controller: CategoryController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        discount_source_items: list[DiscountTransferItem],
        discount_target_items: list[DiscountTransferItem],
        on_discount_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_discount_delete_clicked: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__buttons_spacing_row = ft.Row(height=AppDimensions.SPACE_2XL, visible=mode == ViewMode.EDIT)
        main_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "code", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid, expand=True),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=True),
        ]
        self._columns_row.controls.extend(columns)
        self._init_discount_bulk_transfer(
            mode,
            discount_source_items,
            discount_target_items,
            self._translation.get("discounts"),
            self._translation.get("category_discounts"),
            on_discount_save_clicked,
            on_discount_delete_clicked,
            height=AppDimensions.SECTION_HEIGHT_LARGE,
            visible_modes=set(self._DETAIL_MODES),
        )
        bulk_transfer_row = self._build_discount_bulk_transfer_row()
        self._master_column.controls.extend(
            [self._columns_row, self._spacing_row, self._buttons_row, self.__buttons_spacing_row, bulk_transfer_row]
        )

    def did_mount(self):
        self._mount_discount_bulk_transfer()
        return super().did_mount()

    def set_mode(self, mode: ViewMode) -> None:
        self.__buttons_spacing_row.visible = mode == ViewMode.EDIT
        super().set_mode(mode)
        self._update_discount_bulk_transfer_mode(mode)
        self.safe_update(self.__buttons_spacing_row)
