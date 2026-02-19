from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, cast

import flet as ft
from schemas.business.logistic.item_schema import ItemPlainSchema
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView
from views.controls.date_field_control import DateField
from views.controls.numeric_field_control import NumericField

if TYPE_CHECKING:
    from controllers.core.order_picking_controller import OrderPickingController
    from utils.order_picking_models import OrderPickedItemRow, OrderPickingItemRow


class OrderPickingView(BaseView):
    __MODE_LIST = "list"
    __MODE_PICK = "pick"

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

    __GALLERY_WINDOW_SIZE = 3
    __THUMBNAIL_SIZE = 88

    def __init__(
        self,
        controller: OrderPickingController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        customers: list[tuple[int, str]],
        default_order_date: date | None,
        selected_customer_id: int | None,
    ) -> None:
        super().__init__(controller, translation, mode, view_key, data_row, 0, 0)
        self.__mode = self.__MODE_LIST
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

        self.__title = ft.Text(size=20, weight=ft.FontWeight.BOLD)
        self.__subtitle = ft.Text(size=14)

        order_date_container, _ = self._get_date_picker(
            "order_date",
            4,
            callbacks=[self.__handle_order_date_changed],
            value=default_order_date,
            read_only=False,
        )
        self.__order_date_input = cast(DateField, order_date_container.content)

        customer_container, _ = self._get_dropdown(
            "customer_id",
            4,
            customers,
            callbacks=[self.__handle_customer_changed],
        )
        self.__customer_input = cast(ft.Dropdown, customer_container.content)

        order_container, _ = self._get_dropdown(
            "order_id",
            4,
            [],
            callbacks=[self.__handle_order_changed],
        )
        self.__order_input = cast(ft.Dropdown, order_container.content)

        package_item_container, _ = self._get_dropdown(
            "package_item_id",
            8,
            [],
        )
        package_item_container.col = {"xs": 8.0, "sm": 8.0}
        self.__package_item_input = cast(ft.Dropdown, package_item_container.content)
        self.__package_item_input.disabled = True
        self.__add_package_button = ft.Button(
            on_click=self.__on_add_package_clicked,
            disabled=True,
        )
        package_button_container = ft.Container(
            content=self.__add_package_button,
            col={"xs": 4.0, "sm": 4.0},
            alignment=ft.Alignment.CENTER_LEFT,
        )
        self.__packages_row = ft.ResponsiveRow(
            controls=[package_item_container, package_button_container],
            columns=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        pick_bin_container, _ = self._get_dropdown(
            "pick_bin_id",
            12,
            [],
            callbacks=[self.__handle_pick_bin_changed],
        )
        self.__pick_bin_input = cast(ft.Dropdown, pick_bin_container.content)

        pick_quantity_container, _ = self._get_numeric_input(
            "pick_quantity",
            12,
            value=1,
            step=1,
            precision=0,
            min_value=1,
            is_float=False,
        )
        self.__pick_quantity_input = cast(NumericField, pick_quantity_container.content)

        self._add_to_inputs(
            {
                "order_date": FieldGroup(input=(order_date_container, 4)),
                "customer_id": FieldGroup(input=(customer_container, 4)),
                "order_id": FieldGroup(input=(order_container, 4)),
                "package_item_id": FieldGroup(input=(package_item_container, 8)),
                "pick_bin_id": FieldGroup(input=(pick_bin_container, 12)),
                "pick_quantity": FieldGroup(input=(pick_quantity_container, 12)),
            }
        )

        self.__orders_row = ft.ResponsiveRow(
            controls=[order_date_container, customer_container, order_container],
            columns=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self.__items_list = ft.Column(spacing=8)
        self.__picked_items_header = ft.Text(weight=ft.FontWeight.W_600, size=14)
        self.__picked_items_list = ft.Column(spacing=8)
        self.__picked_items_section = ft.Column(
            controls=[self.__picked_items_header, self.__picked_items_list],
            spacing=8,
        )
        self.__list_section = ft.Column(
            controls=[
                self.__packages_row,
                ft.Divider(height=1),
                self.__items_list,
                ft.Divider(height=1),
                self.__picked_items_section,
            ],
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            visible=True,
        )

        self.__pick_item_title = ft.Text(size=16, weight=ft.FontWeight.W_600)
        self.__pick_details_container = ft.Container()
        self.__pick_gallery_container = ft.Container()
        self.__pick_bin_info_text = ft.Text(size=13)
        self.__pick_buttons_row = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        )

        self.__pick_save_button = ft.Button(on_click=self.__on_pick_save_clicked, width=140)
        self.__pick_back_button = ft.Button(on_click=self.__on_pick_cancel_clicked, width=140)
        self.__pick_buttons_row.controls = [self.__pick_back_button, self.__pick_save_button]

        self.__pick_section = ft.Column(
            controls=[
                self.__pick_item_title,
                pick_bin_container,
                self.__pick_bin_info_text,
                pick_quantity_container,
                self.__pick_buttons_row,
                ft.Divider(height=1),
                self.__pick_details_container,
                ft.Divider(height=1),
                self.__pick_gallery_container,
            ],
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            visible=False,
        )

        self.__back_button = ft.Button(on_click=self.__on_back_to_menu_clicked, width=220)
        self.__header_texts = ft.Column(
            controls=[self.__title, self.__subtitle],
            spacing=2,
            expand=True,
        )
        self.__header_row = ft.Row(
            controls=[
                self.__header_texts,
                ft.Container(content=self.__back_button, alignment=ft.Alignment.CENTER_RIGHT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
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
        self.__render_subtitle()

    def did_mount(self) -> None:
        try:
            self.__pick_quantity_input.read_only = False
        except RuntimeError:
            pass
        super().did_mount()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.__render_subtitle()
        self.__render_items_list()
        if self.__mode == self.__MODE_PICK:
            self.__render_pick_form()
        self.safe_update(self)

    def set_orders(self, orders: list[tuple[int, str]], selected_order_id: int | None) -> None:
        self.__selected_order_id = selected_order_id
        self.__order_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(order_id), text=label) for order_id, label in orders
        ]
        self.__order_input.value = str(selected_order_id) if selected_order_id is not None else "0"
        self.safe_update(self.__order_input)
        self.__render_subtitle()
        self.safe_update(self.__subtitle)

    def reset_order_selection(self) -> None:
        self.__selected_order_id = None
        self.__order_input.value = "0"
        self.safe_update(self.__order_input)
        self.__render_subtitle()
        self.safe_update(self.__subtitle)

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
        self.__mode = self.__MODE_LIST
        self.__orders_row.visible = True
        self.__pick_section.visible = False
        self.__list_section.visible = True
        self.__back_button.visible = True
        self.__render_static_texts()
        self.__render_subtitle()
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
        self.__mode = self.__MODE_PICK
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
        self.__render_subtitle()
        self.__render_pick_form()
        self.safe_update(self)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("order_picking")
        self.__order_input.label = self._translation.get("order")
        self.__customer_input.label = self._translation.get("customer")
        self.__picked_items_header.value = self._translation.get("picked_items")
        self.__package_item_input.label = self._translation.get("packages")
        self.__add_package_button.content = self._translation.get("add_package")
        self.__pick_bin_input.label = self._translation.get("source_bin")
        self.__back_button.content = self._translation.get("back_to_menu")
        self.__pick_back_button.content = self._translation.get("back")
        self.__pick_save_button.content = self._translation.get("save")

    def __render_subtitle(self) -> None:
        if self.__mode == self.__MODE_PICK and self.__pick_item is not None:
            self.__subtitle.value = self.__pick_item.name
            return
        if self.__selected_order_id is None:
            self.__subtitle.value = self._translation.get("select_order")
            return
        self.__subtitle.value = f"{self._translation.get('order')}: {self.__selected_order_id}"

    def __render_items_list(self) -> None:
        if not self.__order_rows:
            self.__items_list.controls = [
                ft.Text(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER),
            ]
        else:
            controls: list[ft.Control] = []
            for row in self.__order_rows:
                controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(row.item_name),
                            subtitle=ft.Text(
                                f"{self._translation.get('index')}: {row.item_index} | "
                                f"{self._translation.get('to_process')}: {row.to_process}"
                            ),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                            on_click=self.__build_item_click_handler(row.item_id),
                        )
                    )
                )
            self.__items_list.controls = controls

        if not self.__picked_rows:
            self.__picked_items_list.controls = [
                ft.Text(self._translation.get("no_picked_items"), text_align=ft.TextAlign.CENTER),
            ]
        else:
            picked_controls: list[ft.Control] = []
            for row in self.__picked_rows:
                picked_controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(row.item_name),
                            subtitle=ft.Text(
                                f"{self._translation.get('index')}: {row.item_index} | "
                                f"{self._translation.get('location')}: {row.bin_location} | "
                                f"{self._translation.get('quantity')}: {row.quantity}"
                            ),
                        )
                    )
                )
            self.__picked_items_list.controls = picked_controls

        self.__picked_items_header.value = self._translation.get("picked_items")
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
        labels_column = ft.Column(
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2),
                    content=ft.Text(f"{label}:", weight=ft.FontWeight.W_600),
                )
                for label, _ in detail_rows
            ],
            tight=True,
            spacing=2,
            width=150,
        )
        values_column = ft.Column(
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2),
                    content=ft.Text(value, selectable=True),
                )
                for _, value in detail_rows
            ],
            tight=True,
            spacing=2,
            expand=True,
        )
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=2, vertical=2),
            content=ft.Row(
                controls=[labels_column, values_column],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
        )

    def __build_gallery_section(self, image_urls: list[str]) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text(self._translation.get("images"), weight=ft.FontWeight.W_600),
                self.__build_gallery_control(image_urls),
            ],
            tight=True,
            spacing=6,
        )

    def __build_gallery_control(self, image_urls: list[str]) -> ft.Control:
        if not image_urls:
            self.__gallery_image_urls = []
            self.__gallery_thumbnails_row = None
            self.__gallery_left_button = None
            self.__gallery_right_button = None
            return ft.Container(
                content=ft.Text(self._translation.get("no_images"), text_align=ft.TextAlign.CENTER),
                padding=ft.Padding.symmetric(vertical=8),
            )
        self.__gallery_image_urls = list(image_urls)
        self.__gallery_thumbnails_row = ft.Row(spacing=8, run_spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        self.__gallery_left_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            on_click=self.__move_gallery_left,
            disabled=True,
        )
        self.__gallery_right_button = ft.IconButton(
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
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def __move_gallery_left(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index <= 0:
            return
        self.__gallery_start_index -= 1
        self.__render_gallery_thumbnails()

    def __move_gallery_right(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls):
            return
        self.__gallery_start_index += 1
        self.__render_gallery_thumbnails()

    def __render_gallery_thumbnails(self) -> None:
        if self.__gallery_thumbnails_row is None:
            return
        self.__gallery_thumbnails_row.controls.clear()
        window = self.__gallery_image_urls[
            self.__gallery_start_index : self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE
        ]
        for url in window:
            self.__gallery_thumbnails_row.controls.append(
                ft.Container(
                    width=self.__THUMBNAIL_SIZE,
                    height=self.__THUMBNAIL_SIZE,
                    content=ft.Image(
                        src=url,
                        width=self.__THUMBNAIL_SIZE,
                        height=self.__THUMBNAIL_SIZE,
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
            self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls)
        )
        self.safe_update(self.__gallery_left_button)
        self.safe_update(self.__gallery_right_button)

    def __open_image_dialog(self, url: str) -> None:
        dialog = BaseDialog(
            title=None,
            controls=[
                ft.Container(
                    width=320,
                    height=420,
                    content=ft.Image(src=url, width=320, height=420, fit=ft.BoxFit.CONTAIN),
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
        self.__render_subtitle()
        self.safe_update(self.__subtitle)
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
