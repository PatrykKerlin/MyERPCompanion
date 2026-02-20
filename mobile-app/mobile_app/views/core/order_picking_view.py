from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import flet as ft
from schemas.business.logistic.item_schema import ItemPlainSchema
from styles.styles import (
    AlignmentStyles,
    ButtonStyles,
    MobileCommonViewStyles,
    OrderPickingViewStyles,
    TypographyStyles,
)
from utils.enums import View
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.order_picking_controller import OrderPickingController
    from utils.order_picking_models import OrderPickedItemRow, OrderPickingItemRow


class OrderPickingView(BaseView):
    __META_FIELDS = {
        "id",
        "created_at",
        "created_by",
        "modified_at",
        "modified_by",
        "created_by_username",
        "modified_by_username",
    }
    __FINANCIAL_FIELDS = {
        "supplier_id",
        "purchase_price",
        "vat_rate",
        "margin",
        "lead_time",
        "moq",
        "total_net",
        "total_vat",
        "total_gross",
        "total_discount",
    }
    __BIN_AND_DISCOUNT_FIELDS = {
        "bin_ids",
        "bins",
        "discount_ids",
        "discounts",
    }
    __HIDDEN_DETAIL_FIELDS = {
        "category_id",
        "unit_id",
        "is_available",
        "is_returnable",
        "min_stock_level",
        "max_stock_level",
        "to_process",
        "is_active",
        "is_package",
    }
    __DETAIL_FIELDS_ORDER = [
        "index",
        "name",
        "ean",
        "description",
        "category_name",
        "unit_name",
        "is_fragile",
        "stock_quantity",
        "reserved_quantity",
        "outbound_quantity",
        "width",
        "height",
        "length",
        "weight",
        "expiration_date",
    ]

    def __init__(
        self,
        controller: OrderPickingController,
        translation: Translation,
        view_key: View,
        customers: list[tuple[int, str]],
        default_order_date: date | None,
        selected_customer_id: int | None,
    ) -> None:
        super().__init__(controller, translation, view_key)
        self.__order_rows: list[OrderPickingItemRow] = []
        self.__picked_rows: list[OrderPickedItemRow] = []
        self.__selected_order_id: int | None = None

        self.__pick_item: ItemPlainSchema | None = None
        self.__pick_is_package = False
        self.__pick_to_process: int = 0
        self.__pick_bin_outbound_by_id: dict[int, int] = {}
        self.__pick_bin_available_by_id: dict[int, int] = {}
        self.__pick_unit_name: str | None = None
        self.__gallery_start_index = 0
        self.__gallery_image_urls: list[str] = []
        self.__gallery_thumbnails_row: ft.Row | None = None
        self.__gallery_left_button: ft.IconButton | None = None
        self.__gallery_right_button: ft.IconButton | None = None

        self.__title = self._get_label("", style=TypographyStyles.HEADER_TITLE)

        self.__order_date_input = self._get_date_field(
            value=default_order_date,
            on_change=lambda event: self._controller.on_value_changed("order_date", self.__handle_order_date_changed),
            expand=True,
            read_only=False,
        )
        self.__order_date_input.col = self._responsive_col(OrderPickingViewStyles.ORDER_DATE_INPUT_SIZE)

        self.__customer_input = self._get_dropdown(
            options=customers,
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("customer_id", self.__handle_customer_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__customer_input.col = self._responsive_col(OrderPickingViewStyles.CUSTOMER_INPUT_SIZE)

        self.__order_input = self._get_dropdown(
            options=[],
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("order_id", self.__handle_order_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__order_input.col = self._responsive_col(OrderPickingViewStyles.ORDER_INPUT_SIZE)

        self.__package_item_input = self._get_dropdown(
            options=[],
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("package_item_id"),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__package_item_input.col = OrderPickingViewStyles.PACKAGE_ITEM_COL
        self.__package_item_input.disabled = True
        self.__add_package_button = self._get_button(
            on_click=self.__on_add_package_clicked,
            disabled=True,
        )
        package_button_container = ft.Container(
            content=self.__add_package_button,
            col=OrderPickingViewStyles.PACKAGE_BUTTON_COL,
            alignment=AlignmentStyles.CENTER_LEFT,
        )
        self.__packages_row = ft.ResponsiveRow(
            controls=[self.__package_item_input, package_button_container],
            columns=OrderPickingViewStyles.PACKAGE_ROW_COLUMNS,
            alignment=OrderPickingViewStyles.PACKAGE_ROW_ALIGNMENT,
            vertical_alignment=OrderPickingViewStyles.PACKAGE_ROW_VERTICAL_ALIGNMENT,
        )

        self.__pick_bin_input = self._get_dropdown(
            options=[],
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("pick_bin_id", self.__handle_pick_bin_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__pick_bin_input.col = self._responsive_col(OrderPickingViewStyles.PICK_BIN_INPUT_SIZE)

        self.__pick_quantity_input = self._get_numeric_field(
            value=1,
            step=1,
            precision=0,
            min_value=1,
            is_float=False,
            on_change=lambda event: self._controller.on_value_changed("pick_quantity"),
            expand=True,
        )
        self.__pick_quantity_input.col = self._responsive_col(OrderPickingViewStyles.PICK_QUANTITY_INPUT_SIZE)

        self._add_to_inputs(
            {
                "order_date": self.__order_date_input,
                "customer_id": self.__customer_input,
                "order_id": self.__order_input,
                "package_item_id": self.__package_item_input,
                "pick_bin_id": self.__pick_bin_input,
                "pick_quantity": self.__pick_quantity_input,
            }
        )

        self.__orders_row = ft.ResponsiveRow(
            controls=[self.__order_date_input, self.__customer_input, self.__order_input],
            columns=OrderPickingViewStyles.ORDERS_ROW_COLUMNS,
            alignment=OrderPickingViewStyles.ORDERS_ROW_ALIGNMENT,
            vertical_alignment=OrderPickingViewStyles.ORDERS_ROW_VERTICAL_ALIGNMENT,
        )

        self.__items_header = self._get_label("", style=TypographyStyles.PENDING_TITLE)
        self.__items_list = ft.Column(spacing=MobileCommonViewStyles.LIST_SPACING)
        self.__picked_items_header = self._get_label("", style=TypographyStyles.PENDING_TITLE)
        self.__picked_items_list = ft.Column(spacing=MobileCommonViewStyles.LIST_SPACING)
        self.__picked_items_section = ft.Column(
            controls=[self.__picked_items_header, self.__picked_items_list],
            spacing=MobileCommonViewStyles.SECTION_SPACING,
        )
        self.__list_section = ft.Column(
            controls=[
                self.__packages_row,
                ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
                self.__items_header,
                self.__items_list,
                ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
                self.__picked_items_section,
            ],
            expand=True,
            spacing=MobileCommonViewStyles.SECTION_SPACING,
            scroll=ft.ScrollMode.AUTO,
            visible=True,
        )

        self.__pick_item_title = self._get_label("", style=TypographyStyles.SUMMARY_TITLE)
        self.__pick_details_container = ft.Container()
        self.__pick_gallery_container = ft.Container()
        self.__pick_bin_info_text = self._get_label("", style=TypographyStyles.HEADER_SUBTITLE)
        self.__pick_save_button = self._get_button(
            on_click=self.__on_pick_save_clicked,
            style=ButtonStyles.primary_regular,
        )
        self.__pick_back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_pick_cancel_clicked,
            style=ButtonStyles.regular,
        )
        self.__pick_buttons_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.__pick_back_button, col=OrderPickingViewStyles.PICK_BACK_BUTTON_COL),
                ft.Container(content=self.__pick_save_button, col=OrderPickingViewStyles.PICK_SAVE_BUTTON_COL),
            ],
            columns=OrderPickingViewStyles.PICK_BUTTONS_ROW_COLUMNS,
            alignment=OrderPickingViewStyles.PICK_BUTTONS_ROW_ALIGNMENT,
            vertical_alignment=OrderPickingViewStyles.PICK_BUTTONS_ROW_VERTICAL_ALIGNMENT,
        )

        self.__pick_section = ft.Column(
            controls=[
                self.__pick_item_title,
                self.__pick_bin_input,
                self.__pick_bin_info_text,
                self.__pick_quantity_input,
                self.__pick_buttons_row,
                ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
                self.__pick_details_container,
                ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
                self.__pick_gallery_container,
            ],
            expand=True,
            spacing=MobileCommonViewStyles.SECTION_SPACING,
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )

        self.__back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_back_to_menu_clicked,
            style=ButtonStyles.primary_regular,
        )
        self.__header_texts = ft.Column(
            controls=[self.__title],
            spacing=MobileCommonViewStyles.HEADER_TEXTS_SPACING,
        )
        self.__header_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.__header_texts, col=MobileCommonViewStyles.HEADER_TEXTS_COL),
                ft.Container(
                    content=self.__back_button,
                    col=MobileCommonViewStyles.HEADER_ACTION_COL,
                    alignment=MobileCommonViewStyles.HEADER_BACK_ALIGNMENT,
                ),
            ],
            columns=MobileCommonViewStyles.HEADER_ROW_COLUMNS,
            alignment=MobileCommonViewStyles.HEADER_ROW_ALIGNMENT,
            vertical_alignment=MobileCommonViewStyles.HEADER_ROW_VERTICAL_ALIGNMENT,
        )

        self._master_column.controls = [
            self.__header_row,
            self.__orders_row,
            self.__list_section,
            self.__pick_section,
        ]

        if selected_customer_id is not None:
            self.__customer_input.value = str(selected_customer_id)
        else:
            self.__customer_input.value = "0"

        self.__render_static_texts()

    def did_mount(self) -> None:
        try:
            self.__pick_quantity_input.read_only = False
        except RuntimeError:
            pass
        super().did_mount()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.__render_items_list()
        if self.__pick_section.visible:
            self.__render_pick_form()
        self.safe_update(self)

    def set_orders(self, orders: list[tuple[int, str]], selected_order_id: int | None) -> None:
        self.__selected_order_id = selected_order_id
        self.__order_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(order_id), text=label) for order_id, label in orders
        ]
        self.__order_input.value = str(selected_order_id) if selected_order_id is not None else "0"
        self.safe_update(self.__order_input)

    def reset_order_selection(self) -> None:
        self.__selected_order_id = None
        self.__order_input.value = "0"
        self.safe_update(self.__order_input)

    def set_order_items(self, rows: list[OrderPickingItemRow]) -> None:
        self.__order_rows = rows
        self.__render_items_list()

    def set_picked_items(self, rows: list[OrderPickedItemRow]) -> None:
        self.__picked_rows = rows
        self.__render_items_list()

    def set_package_options(self, options: list[tuple[int, str]], enabled: bool) -> None:
        self.__package_item_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(item_id), text=label) for item_id, label in options
        ]
        if enabled and options:
            valid_keys = {str(item_id) for item_id, _ in options}
            current_value = self.__package_item_input.value
            self.__package_item_input.value = current_value if current_value in valid_keys else str(options[0][0])
        else:
            self.__package_item_input.value = "0"
        disabled = (not enabled) or (not options)
        self.__package_item_input.disabled = disabled
        self.__add_package_button.disabled = disabled
        self.safe_update(self.__package_item_input)
        self.safe_update(self.__add_package_button)

    def show_items_list(self) -> None:
        self.__orders_row.visible = True
        self.__pick_section.visible = False
        self.__list_section.visible = True
        self.__back_button.visible = True
        self.__render_static_texts()
        self.__render_items_list()
        self.safe_update(self)

    def show_pick_form(
        self,
        item: ItemPlainSchema,
        to_process: int,
        bin_options: list[tuple[int, str, int, int]],
        default_bin_id: int,
        default_quantity: int,
        unit_name: str | None,
        is_package_pick: bool,
    ) -> None:
        self.__pick_item = item
        self.__pick_is_package = is_package_pick
        self.__pick_to_process = max(0, to_process)
        self.__pick_unit_name = unit_name
        self.__gallery_start_index = 0
        self.__pick_bin_outbound_by_id = {bin_id: outbound for bin_id, _, outbound, _ in bin_options}
        self.__pick_bin_available_by_id = {bin_id: available for bin_id, _, _, available in bin_options}

        self.__pick_bin_input.options = [
            ft.dropdown.Option(
                key=str(bin_id),
                text=location,
            )
            for bin_id, location, _outbound, _available in bin_options
        ]

        if default_bin_id in self.__pick_bin_available_by_id:
            self.__pick_bin_input.value = str(default_bin_id)
        elif bin_options:
            self.__pick_bin_input.value = str(bin_options[0][0])
        else:
            self.__pick_bin_input.value = None

        max_quantity = self.__selected_bin_available()
        if max_quantity < 1:
            max_quantity = 1
        normalized_quantity = max(1, min(default_quantity, max_quantity))
        self.__pick_quantity_input.set_limits(1, max_quantity)
        self.__pick_quantity_input.value = normalized_quantity
        self.__update_pick_bin_info()

        self.__orders_row.visible = False
        self.__list_section.visible = False
        self.__pick_section.visible = True
        self.__back_button.visible = False

        self.__render_static_texts()
        self.__render_pick_form()
        self.safe_update(self)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("order_picking")
        self.__order_input.label = self._translation.get("order")
        self.__customer_input.label = self._translation.get("customer")
        self.__items_header.value = self._translation.get("items_to_pick")
        self.__picked_items_header.value = self._translation.get("picked_items")
        self.__package_item_input.label = self._translation.get("packages")
        self.__add_package_button.content = self._translation.get("add")
        self.__pick_bin_input.label = self._translation.get("source_bin")
        self.__back_button.content = self._translation.get("back")
        self.__pick_back_button.content = self._translation.get("back")
        self.__pick_save_button.content = self._translation.get("add")

    def __render_items_list(self) -> None:
        if not self.__order_rows:
            self.__items_list.controls = [
                self._get_label(self._translation.get("no_items_to_pick"), text_align=ft.TextAlign.CENTER),
            ]
        else:
            controls: list[ft.Control] = []
            for row in self.__order_rows:
                controls.append(
                    ft.Card(
                        bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                        content=ft.ListTile(
                            title=self._get_label(row.item_name),
                            subtitle=self._get_label(
                                f"{self._translation.get('index')}: {row.item_index} | "
                                f"{self._translation.get('to_process')}: {row.to_process}"
                            ),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                            on_click=self.__build_item_click_handler(row.item_id),
                        ),
                    )
                )
            self.__items_list.controls = controls

        if not self.__picked_rows:
            self.__picked_items_list.controls = [
                self._get_label(self._translation.get("no_picked_items"), text_align=ft.TextAlign.CENTER),
            ]
        else:
            picked_controls: list[ft.Control] = []
            for row in self.__picked_rows:
                picked_controls.append(
                    ft.Card(
                        bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                        content=ft.ListTile(
                            title=self._get_label(row.item_name),
                            subtitle=self._get_label(
                                f"{self._translation.get('index')}: {row.item_index} | "
                                f"{self._translation.get('location')}: {row.bin_location} | "
                                f"{self._translation.get('quantity')}: {row.quantity}"
                            ),
                        ),
                    )
                )
            self.__picked_items_list.controls = picked_controls

        self.__items_header.value = self._translation.get("items_to_pick")
        self.__picked_items_header.value = self._translation.get("picked_items")
        self.safe_update(self.__items_header)
        self.safe_update(self.__items_list)
        self.safe_update(self.__picked_items_header)
        self.safe_update(self.__picked_items_list)

    def __render_pick_form(self) -> None:
        if self.__pick_item is None:
            return
        self.__pick_item_title.value = f"{self._translation.get('index')}: {self.__pick_item.index}"
        detail_rows = self.__build_detail_rows(self.__pick_item)
        self.__pick_details_container.content = self.__build_detail_columns(detail_rows)
        image_urls = self.__image_urls_for_item(self.__pick_item)
        self.__pick_gallery_container.content = self.__build_gallery_section(image_urls)
        self.__update_pick_bin_info()

        self.safe_update(self.__pick_item_title)
        self.safe_update(self.__pick_bin_info_text)
        self.safe_update(self.__pick_gallery_container)
        self.safe_update(self.__pick_details_container)
        self.safe_update(self.__pick_bin_input)
        self.safe_update(self.__pick_quantity_input)

    def __build_detail_rows(self, item: ItemPlainSchema) -> list[tuple[str, str]]:
        data = item.model_dump()
        data["unit_name"] = self.__pick_unit_name if self.__pick_unit_name else str(item.unit_id)
        rows: list[tuple[str, str]] = []
        used_keys: set[str] = set()

        for key in self.__DETAIL_FIELDS_ORDER:
            if key not in data or self.__is_excluded_field(key):
                continue
            rows.append((key, self.__format_value(data[key])))
            used_keys.add(key)

        for key, value in data.items():
            if key in used_keys or self.__is_excluded_field(key):
                continue
            rows.append((key, self.__format_value(value)))

        return rows

    def __is_excluded_field(self, key: str) -> bool:
        return (
            key == "images"
            or key in self.__META_FIELDS
            or key in self.__FINANCIAL_FIELDS
            or key in self.__BIN_AND_DISCOUNT_FIELDS
            or key in self.__HIDDEN_DETAIL_FIELDS
        )

    def __format_value(self, value: Any) -> str:
        if value is None:
            return "-"
        if isinstance(value, bool):
            return self._translation.get("yes") if value else self._translation.get("no")
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, float):
            return f"{value:g}"
        if isinstance(value, list):
            if not value:
                return "-"
            return ", ".join(str(item) for item in value)
        return str(value)

    def __build_detail_columns(self, detail_rows: list[tuple[str, str]]) -> ft.Control:
        rows: list[ft.Control] = [
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col=OrderPickingViewStyles.DETAILS_LABEL_COL,
                        padding=OrderPickingViewStyles.DETAILS_LABEL_PADDING,
                        content=self._get_label(f"{label}:", style=TypographyStyles.DETAIL_LABEL),
                    ),
                    ft.Container(
                        col=OrderPickingViewStyles.DETAILS_VALUE_COL,
                        padding=OrderPickingViewStyles.DETAILS_VALUE_PADDING,
                        content=self._get_label(value, selectable=True),
                    ),
                ],
                columns=OrderPickingViewStyles.DETAILS_PAIR_COLUMNS,
                alignment=AlignmentStyles.AXIS_START,
                vertical_alignment=AlignmentStyles.CROSS_START,
            )
            for label, value in detail_rows
        ]
        return ft.Container(
            padding=OrderPickingViewStyles.DETAILS_WRAPPER_PADDING,
            content=ft.Column(
                controls=rows,
                spacing=OrderPickingViewStyles.DETAILS_COL_SPACING,
                tight=True,
            ),
        )

    def __build_gallery_section(self, image_urls: list[str]) -> ft.Control:
        return ft.Column(
            controls=[
                self._get_label(self._translation.get("images"), style=TypographyStyles.SECTION_TITLE),
                self.__build_gallery_control(image_urls),
            ],
            tight=True,
            spacing=OrderPickingViewStyles.GALLERY_SECTION_SPACING,
        )

    def __build_gallery_control(self, image_urls: list[str]) -> ft.Control:
        if not image_urls:
            self.__gallery_image_urls = []
            self.__gallery_thumbnails_row = None
            self.__gallery_left_button = None
            self.__gallery_right_button = None
            return ft.Container(
                content=self._get_label(self._translation.get("no_images"), text_align=ft.TextAlign.CENTER),
                padding=OrderPickingViewStyles.GALLERY_EMPTY_PADDING,
            )
        self.__gallery_image_urls = list(image_urls)
        self.__gallery_thumbnails_row = ft.Row(
            spacing=OrderPickingViewStyles.GALLERY_THUMB_ROW_SPACING,
            run_spacing=OrderPickingViewStyles.GALLERY_THUMB_ROW_RUN_SPACING,
            alignment=OrderPickingViewStyles.GALLERY_THUMB_ROW_ALIGNMENT,
        )
        self.__gallery_left_button = self._get_icon_button(
            icon=ft.Icons.CHEVRON_LEFT,
            on_click=self.__move_gallery_left,
            disabled=True,
        )
        self.__gallery_right_button = self._get_icon_button(
            icon=ft.Icons.CHEVRON_RIGHT,
            on_click=self.__move_gallery_right,
            disabled=True,
        )
        self.__render_gallery_thumbnails()
        return ft.Row(
            controls=[
                self.__gallery_left_button,
                ft.Container(content=self.__gallery_thumbnails_row, expand=True),
                self.__gallery_right_button,
            ],
            spacing=OrderPickingViewStyles.GALLERY_CONTROL_SPACING,
            vertical_alignment=AlignmentStyles.CROSS_CENTER,
        )

    def __move_gallery_left(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index <= 0:
            return
        self.__gallery_start_index -= 1
        self.__render_gallery_thumbnails()

    def __move_gallery_right(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index + OrderPickingViewStyles.GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls):
            return
        self.__gallery_start_index += 1
        self.__render_gallery_thumbnails()

    def __render_gallery_thumbnails(self) -> None:
        if self.__gallery_thumbnails_row is None:
            return
        self.__gallery_thumbnails_row.controls.clear()
        window = self.__gallery_image_urls[
            self.__gallery_start_index : self.__gallery_start_index + OrderPickingViewStyles.GALLERY_WINDOW_SIZE
        ]
        for url in window:
            self.__gallery_thumbnails_row.controls.append(
                ft.Container(
                    width=OrderPickingViewStyles.GALLERY_THUMB_SIZE,
                    height=OrderPickingViewStyles.GALLERY_THUMB_SIZE,
                    content=ft.Image(
                        src=url,
                        width=OrderPickingViewStyles.GALLERY_THUMB_SIZE,
                        height=OrderPickingViewStyles.GALLERY_THUMB_SIZE,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                    on_click=lambda _, image_url=url: self.__open_image_dialog(image_url),
                )
            )
        self.safe_update(self.__gallery_thumbnails_row)
        self.__update_gallery_buttons()

    def __update_gallery_buttons(self) -> None:
        if self.__gallery_left_button is None or self.__gallery_right_button is None:
            return
        self.__gallery_left_button.disabled = self.__gallery_start_index <= 0
        self.__gallery_right_button.disabled = (
            self.__gallery_start_index + OrderPickingViewStyles.GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls)
        )
        self.safe_update(self.__gallery_left_button)
        self.safe_update(self.__gallery_right_button)

    def __open_image_dialog(self, url: str) -> None:
        dialog = BaseDialog(
            title=None,
            controls=[
                ft.Container(
                    width=OrderPickingViewStyles.GALLERY_DIALOG_IMAGE_WIDTH,
                    height=OrderPickingViewStyles.GALLERY_DIALOG_IMAGE_HEIGHT,
                    content=ft.Image(
                        src=url,
                        width=OrderPickingViewStyles.GALLERY_DIALOG_IMAGE_WIDTH,
                        height=OrderPickingViewStyles.GALLERY_DIALOG_IMAGE_HEIGHT,
                        fit=ft.BoxFit.CONTAIN,
                    ),
                )
            ],
            actions=[ft.TextButton(self._translation.get("close"), on_click=lambda _: self.__close_dialog())],
        )
        self.queue_dialog(dialog)

    def __close_dialog(self) -> None:
        try:
            self.page.pop_dialog()
        except RuntimeError:
            return

    @staticmethod
    def __image_urls_for_item(item: ItemPlainSchema) -> list[str]:
        ordered_images = sorted(item.images, key=lambda image: image.order)
        return [image.url for image in ordered_images if image.url]

    def __handle_order_date_changed(self) -> None:
        selected_date = self.__order_date_input.value
        self._controller.on_order_date_changed(selected_date.isoformat() if selected_date else None)

    def __handle_customer_changed(self) -> None:
        self._controller.on_customer_changed(self.__customer_input.value)

    def __handle_order_changed(self) -> None:
        self.__selected_order_id = self.__parse_optional_int(self.__order_input.value)
        self._controller.on_order_selected(self.__selected_order_id)

    def __handle_pick_bin_changed(self) -> None:
        max_quantity = self.__selected_bin_available()
        if max_quantity < 1:
            max_quantity = 1
        current_quantity = self.__parse_quantity(self.__pick_quantity_input.value) or 1
        self.__pick_quantity_input.set_limits(1, max_quantity)
        self.__pick_quantity_input.value = max(1, min(current_quantity, max_quantity))
        self.__update_pick_bin_info()
        self.safe_update(self.__pick_quantity_input)
        self.safe_update(self.__pick_bin_info_text)

    def __update_pick_bin_info(self) -> None:
        selected_bin_id = self.__parse_optional_int(self.__pick_bin_input.value)
        outbound_available = (
            self.__pick_bin_outbound_by_id.get(selected_bin_id, 0) if selected_bin_id is not None else 0
        )
        if self.__pick_is_package:
            self.__pick_bin_info_text.value = f"{self._translation.get('available')}: {outbound_available}"
        else:
            self.__pick_bin_info_text.value = (
                f"{self._translation.get('available')}: {outbound_available} | "
                f"{self._translation.get('to_process')}: {self.__pick_to_process}"
            )

    def __selected_bin_available(self) -> int:
        selected_bin_id = self.__parse_optional_int(self.__pick_bin_input.value)
        if selected_bin_id is None:
            return 0
        return self.__pick_bin_available_by_id.get(selected_bin_id, 0)

    def __on_back_to_menu_clicked(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_back_to_menu()

    def __on_pick_cancel_clicked(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_pick_form_cancelled()

    def __on_pick_save_clicked(self, _: ft.Event[ft.Button]) -> None:
        selected_bin_id = self.__parse_optional_int(self.__pick_bin_input.value)
        quantity = self.__parse_quantity(self.__pick_quantity_input.value)
        self._controller.on_pick_form_saved(selected_bin_id, quantity)

    def __on_add_package_clicked(self, _: ft.Event[ft.Button]) -> None:
        package_item_id = self.__parse_optional_int(self.__package_item_input.value)
        self._controller.on_package_item_selected(package_item_id)

    def __build_item_click_handler(self, item_id: int):
        return lambda _: self._controller.on_order_item_selected(item_id)

    @staticmethod
    def __parse_optional_int(value: str | int | float | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        stripped = value.strip()
        if stripped == "" or stripped == "0":
            return None
        try:
            return int(stripped)
        except ValueError:
            return None

    @staticmethod
    def __parse_quantity(value: int | float | None) -> int | None:
        if value is None:
            return None
        quantity = int(value)
        if quantity <= 0:
            return None
        return quantity
