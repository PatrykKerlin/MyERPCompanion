from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from controllers.base.base_controller import BaseController
from styles.colors import AppColors
from styles.dimensions import AppDimensions, ItemViewDimensions
from styles.styles import AlignmentStyles, ButtonStyles, ControlStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.controls.data_table_control import DataTable
from views.mixins.discount_bulk_transfer_mixin import DiscountBulkTransferMixin, DiscountTransferItem

if TYPE_CHECKING:
    from controllers.business.logistic.item_controller import ItemController


class ItemView(BaseView, DiscountBulkTransferMixin):
    def __init__(
        self,
        controller: ItemController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        categories: list[tuple[int, str]],
        units: list[tuple[int, str]],
        suppliers: list[tuple[int, str]],
        bins: list[dict[str, Any]],
        discount_source_items: list[DiscountTransferItem],
        discount_target_items: list[DiscountTransferItem],
        on_discount_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_discount_delete_clicked: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__GALLERY_HEIGHT = ItemViewDimensions.GALLERY_HEIGHT
        self.__PRIMARY_BORDER = ItemViewDimensions.PRIMARY_BORDER

        product_fields_definitions = [
            {"key": "index", "input": self._get_text_input},
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "ean", "input": self._get_text_input},
            {"key": "category_id", "input": self._get_dropdown, "options": categories},
            {"key": "unit_id", "input": self._get_dropdown, "options": units},
        ]
        financial_fields_definitions = [
            {"key": "supplier_id", "input": self._get_dropdown, "options": suppliers},
            {"key": "purchase_price", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "vat_rate", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "margin", "input": self._get_numeric_input, "is_float": True, "step": 0.001, "precision": 3},
            {"key": "moq", "input": self._get_numeric_input},
            {"key": "lead_time", "input": self._get_numeric_input},
        ]
        param_fields_definitions = [
            {"key": "is_available", "input": self._get_checkbox, "value": True, "input_size": 1},
            {"key": "is_fragile", "input": self._get_checkbox, "value": False, "input_size": 1},
            {"key": "is_package", "input": self._get_checkbox, "value": False, "input_size": 1},
            {"key": "is_returnable", "input": self._get_checkbox, "value": False, "input_size": 1},
        ]
        dimensions_fields_definitions = [
            {"key": "width", "input": self._get_numeric_input, "is_float": True, "step": 0.001, "precision": 3},
            {"key": "height", "input": self._get_numeric_input, "is_float": True, "step": 0.001, "precision": 3},
            {"key": "length", "input": self._get_numeric_input, "is_float": True, "step": 0.001, "precision": 3},
            {"key": "weight", "input": self._get_numeric_input, "is_float": True, "step": 0.001, "precision": 3},
            {"key": "expiration_date", "input": self._get_date_picker},
        ]
        stock_fields_definitions = [
            {"key": "stock_quantity", "input": self._get_numeric_input},
            {"key": "reserved_quantity", "input": self._get_numeric_input},
            {"key": "outbound_quantity", "input": self._get_numeric_input},
            {"key": "min_stock_level", "input": self._get_numeric_input},
            {"key": "max_stock_level", "input": self._get_numeric_input},
        ]

        product_fields = self._build_field_groups(product_fields_definitions)
        financial_fields = self._build_field_groups(financial_fields_definitions)
        param_fields = self._build_field_groups(param_fields_definitions)
        dimensions_fields = self._build_field_groups(dimensions_fields_definitions)
        stock_fields = self._build_field_groups(stock_fields_definitions)

        self._add_to_inputs(product_fields, financial_fields, param_fields, dimensions_fields, stock_fields)
        main_grid = self._build_grid(product_fields)
        financial_grid = self._build_grid(financial_fields)
        param_grid = self._build_grid(param_fields)
        dimensions_grid = self._build_grid(dimensions_fields)
        stock_grid = self._build_grid(stock_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=5)

        columns = [
            ft.Column(
                controls=main_grid + financial_grid + stock_grid,
                expand=True,
            ),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + dimensions_grid
                + self._spacing_responsive_row
                + param_grid,
                expand=True,
            ),
        ]
        self._columns_row.controls.extend(columns)

        self.__image_gallery = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=AppDimensions.SPACE_MD,
            vertical_alignment=AlignmentStyles.CROSS_CENTER,
            expand=True,
        )
        self.__image_gallery_container = ft.Container(
            content=self.__image_gallery,
            height=self.__GALLERY_HEIGHT,
            alignment=AlignmentStyles.CENTER_LEFT,
        )
        self.__add_image_button = ft.IconButton(
            icon=ft.Icons.ADD_A_PHOTO,
            on_click=self.__on_add_image_clicked,
            tooltip=self._translation.get("add_image"),
            visible=False,
            width=AppDimensions.ICON_BUTTON_WIDTH,
            style=ButtonStyles.icon,
        )
        self.__bins_table = DataTable(
            columns=["id", "location", "quantity"],
            rows=bins,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            translation=self._translation,
            height=AppDimensions.SECTION_HEIGHT_LARGE,
            with_button=False,
        )
        self.__image_order_field = ft.TextField(
            label=self._translation.get("sequence"),
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.__image_order_field.border_radius = ControlStyles.FIELD_BORDER_RADIUS
        self.__image_order_field.border_color = ControlStyles.FIELD_BORDER_COLOR
        self.__image_order_field.focused_border_color = ControlStyles.FIELD_FOCUSED_BORDER_COLOR
        self.__image_order_field.height = ControlStyles.TEXT_FIELD_HEIGHT
        self.__image_order_field.content_padding = ControlStyles.FIELD_PADDING
        self.__image_primary_checkbox = ft.Checkbox(
            label=self._translation.get("is_primary"),
        )
        dialog_buttons = [
            ft.TextButton(
                self._translation.get("delete"),
                on_click=self.__on_image_delete_requested,
                style=ButtonStyles.compact,
            ),
            ft.TextButton(
                self._translation.get("cancel"),
                on_click=self.__on_image_edit_cancelled,
                style=ButtonStyles.compact,
            ),
            ft.Button(
                self._translation.get("save"),
                on_click=self.__on_image_edit_confirmed,
                style=ButtonStyles.compact,
            ),
        ]
        self.__image_edit_dialog = ft.AlertDialog(
            title=ft.Text(self._translation.get("edit_image")),
            content=ft.Column(
                controls=[self.__image_order_field, self.__image_primary_checkbox],
                tight=True,
            ),
            actions=dialog_buttons,
        )
        self.__selected_image_id: int | None = None
        self.__gallery_column = ft.Column(
            controls=[
                self.__image_gallery_container,
                ft.Row(
                    controls=[self.__add_image_button],
                    alignment=AlignmentStyles.AXIS_END,
                ),
                self.__bins_table,
            ],
            expand=True,
        )
        self._init_discount_bulk_transfer(
            mode,
            discount_source_items,
            discount_target_items,
            self._translation.get("discounts"),
            self._translation.get("item_discounts"),
            on_discount_save_clicked,
            on_discount_delete_clicked,
            height=AppDimensions.SECTION_HEIGHT_LARGE,
        )
        bulk_transfer_row = self._build_discount_bulk_transfer_row()
        self._rows = [
            self._columns_row,
            self.__gallery_column,
            ft.Row(height=AppDimensions.SPACE_2XL),
            bulk_transfer_row,
            self._spacing_row,
            self._buttons_row,
        ]
        self._master_column.controls.extend(self._rows)

    def did_mount(self):
        if self._data_row and self._data_row["images"]:
            self.set_images(self._data_row["images"])
        self._mount_discount_bulk_transfer()
        return super().did_mount()

    def set_images(self, images: list[dict[str, Any]]) -> None:
        images.sort(key=lambda item: item["order"])
        self.__image_gallery.controls = [self.__build_image_control(image) for image in images]
        self.__image_gallery.update()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self.__apply_stock_quantity_rules(mode)
        self._update_discount_bulk_transfer_mode(mode)
        if self._mode not in {ViewMode.READ, ViewMode.EDIT}:
            self.__gallery_column.visible = False
            self.__add_image_button.visible = False
            self.__add_image_button.disabled = True
            self.__bins_table.visible = False
            self.__bins_table.read_only = True
        elif self._mode == ViewMode.EDIT:
            self.__gallery_column.visible = True
            self.__add_image_button.visible = False
            self.__add_image_button.disabled = True
            self.__bins_table.visible = True
            self.__bins_table.read_only = True
        elif self._mode == ViewMode.READ:
            self.__gallery_column.visible = True
            self.__add_image_button.visible = True
            self.__add_image_button.disabled = False
            self.__bins_table.visible = True
            self.__bins_table.read_only = False
        self.__gallery_column.update()

    def __apply_stock_quantity_rules(self, mode: ViewMode) -> None:
        read_only_keys = ("stock_quantity", "reserved_quantity", "outbound_quantity")
        for key in read_only_keys:
            field = self._inputs.get(key)
            if not field:
                continue
            input_control = field.input.content
            if mode == ViewMode.CREATE:
                if hasattr(input_control, "value"):
                    setattr(input_control, "value", 0)
                    if input_control:
                        input_control.update()
                self._controller.set_field_value("stock_quantity", 0)
            if mode in {ViewMode.CREATE, ViewMode.EDIT}:
                if hasattr(input_control, "read_only"):
                    setattr(input_control, "read_only", True)
                if hasattr(input_control, "disabled"):
                    setattr(input_control, "disabled", True)
                if input_control:
                    input_control.update()

    def __build_image_control(self, image: dict[str, Any]) -> ft.Control:
        url = image["url"]
        is_primary = image["is_primary"]
        image_height = self.__GALLERY_HEIGHT - 2 * self.__PRIMARY_BORDER
        padding = self.__PRIMARY_BORDER if is_primary else 0
        border = ft.Border.all(2, AppColors.PRIMARY) if is_primary else None
        return ft.Container(
            content=ft.Image(
                src=url,
                height=image_height,
                fit=ft.BoxFit.CONTAIN,
            ),
            height=self.__GALLERY_HEIGHT,
            padding=padding,
            border=border,
            alignment=AlignmentStyles.CENTER,
            on_click=lambda _: self.__on_image_clicked(image),
        )

    def __on_add_image_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        self._controller.on_image_select_requested()

    def __on_image_clicked(self, image: dict[str, Any]) -> None:
        if self._mode != ViewMode.READ:
            return
        self.__selected_image_id = image["id"]
        self.__image_order_field.value = str(image["order"])
        self.__image_order_field.error = None
        self.__image_primary_checkbox.value = image["is_primary"]
        if self.page:
            BaseController.queue_dialog(self.page, self.__image_edit_dialog)

    def __on_image_edit_cancelled(self, _: ft.Event[ft.TextButton]) -> None:
        self.page.pop_dialog()

    def __on_image_edit_confirmed(self, _: ft.Event[ft.Button]) -> None:
        order_value = (self.__image_order_field.value or "").strip()
        if not order_value.isdigit():
            self.__image_order_field.error = self._translation.get("invalid_value")
            self.__image_order_field.update()
            return
        self.page.pop_dialog()
        if self.__selected_image_id is None:
            return
        self._controller.on_image_update_requested(
            image_id=self.__selected_image_id,
            new_order=int(order_value),
            is_primary=bool(self.__image_primary_checkbox.value),
        )

    def __on_image_delete_requested(self, _: ft.Event[ft.TextButton]) -> None:
        self.page.pop_dialog()
        if self.__selected_image_id is None:
            return
        self._controller.on_image_delete_requested(self.__selected_image_id)
