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

if TYPE_CHECKING:
    from controllers.core.items_controller import ItemsController


class ItemsView(BaseView):
    __MODE_LIST = "list"
    __MODE_DETAILS = "details"

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
    }
    __BIN_AND_DISCOUNT_FIELDS = {
        "bin_ids",
        "bins",
        "discount_ids",
        "discounts",
    }
    __DETAIL_FIELDS_ORDER = [
        "name",
        "index",
        "ean",
        "description",
        "category_name",
        "category_id",
        "unit_id",
        "is_active",
        "is_available",
        "is_fragile",
        "is_package",
        "is_returnable",
        "quantity",
        "stock_quantity",
        "reserved_quantity",
        "outbound_quantity",
        "min_stock_level",
        "max_stock_level",
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
        controller: ItemsController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        item: ItemPlainSchema | None,
        quantity: int,
        items: list[ItemPlainSchema],
        categories: list[tuple[int, str]],
        selected_category_id: int | None,
        index_filter: str,
        caller_view_key: View | None,
    ) -> None:
        super().__init__(controller, translation, mode, view_key, data_row, 0, 0, caller_view_key=caller_view_key)
        self.__mode = self.__MODE_DETAILS if item is not None else self.__MODE_LIST
        self.__item = item
        self.__quantity = quantity
        self.__items = items
        self.__categories = categories
        self.__selected_category_id = selected_category_id
        self.__index_filter = index_filter.strip()
        self.__gallery_start_index = 0

        self.__title = ft.Text(size=20, weight=ft.FontWeight.BOLD)
        self.__subtitle = ft.Text(size=14)
        self.__back_button = ft.Button(on_click=self.__on_back_clicked, width=220)
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

        category_filter_container, _ = self._get_dropdown(
            "category_filter",
            5,
            self.__categories,
            callbacks=[self.__on_category_filter_changed],
        )
        self.__category_filter_input = cast(ft.Dropdown, category_filter_container.content)
        self.__category_filter_input.options = [
            ft.dropdown.Option(key="0", text=self._translation.get("all_categories")),
            *[ft.dropdown.Option(key=str(category_id), text=name) for category_id, name in self.__categories],
        ]
        self.__category_filter_input.value = str(self.__selected_category_id) if self.__selected_category_id else "0"

        index_filter_container, _ = self._get_text_input("index_filter", 7)
        self.__index_filter_input = cast(ft.TextField, index_filter_container.content)
        self.__index_filter_input.value = self.__index_filter
        self.__index_filter_input.on_change = self.__on_index_filter_changed
        self.__index_filter_input.dense = True
        self.__index_filter_input.prefix_icon = ft.Icons.SEARCH

        self._add_to_inputs(
            {
                "category_filter": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(category_filter_container, 5),
                    marker=(ft.Container(), 0),
                ),
                "index_filter": FieldGroup(
                    label=(ft.Container(), 0),
                    input=(index_filter_container, 7),
                    marker=(ft.Container(), 0),
                ),
            }
        )

        self.__filters_row = ft.ResponsiveRow(
            controls=[category_filter_container, index_filter_container],
            columns=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.__items_list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=8)
        self.__list_section = ft.Column(
            controls=[self.__filters_row, ft.Divider(height=1), self.__items_list],
            spacing=8,
            expand=True,
        )

        self.__details = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=8)
        self.__details_section = ft.Column(
            controls=[self.__details],
            spacing=0,
            expand=True,
        )

        self._master_column.controls = [
            self.__header_row,
            ft.Divider(height=1),
            self.__list_section,
            self.__details_section,
        ]
        self.__render()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render()
        self.__update_if_attached()

    def __render(self) -> None:
        if self.__mode == self.__MODE_LIST:
            self.__render_list_mode()
            return
        self.__render_details_mode()

    def __render_list_mode(self) -> None:
        self.__title.value = self._translation.get("items")
        self.__subtitle.value = self._translation.get("select_item")
        self.__back_button.content = self._translation.get("back_to_menu")
        self.__category_filter_input.label = self._translation.get("category")
        self.__category_filter_input.options = [
            ft.dropdown.Option(key="0", text=self._translation.get("all_categories")),
            *[ft.dropdown.Option(key=str(category_id), text=name) for category_id, name in self.__categories],
        ]
        self.__category_filter_input.value = str(self.__selected_category_id) if self.__selected_category_id else "0"
        self.__index_filter_input.label = self._translation.get("index_filter")
        self.__list_section.visible = True
        self.__details_section.visible = False
        self.__items_list.controls = self.__build_list_controls()

    def __render_details_mode(self) -> None:
        self.__title.value = self._translation.get("item_details")
        if self.caller_view_key == View.BINS:
            self.__back_button.content = self._translation.get("back_to_bins")
        else:
            self.__back_button.content = self._translation.get("back_to_items")
        self.__list_section.visible = False
        self.__details_section.visible = True

        if not self.__item:
            self.__subtitle.value = self._translation.get("no_items")
            self.__details.controls = [ft.Text(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]
            return

        self.__subtitle.value = self.__item.name
        image_urls = self.__image_urls()
        max_start_index = max(0, len(image_urls) - self.__GALLERY_WINDOW_SIZE)
        self.__gallery_start_index = min(self.__gallery_start_index, max_start_index)
        detail_rows = self.__build_detail_rows()
        self.__details.controls = [
            self.__build_gallery_section(image_urls),
            ft.Divider(height=1),
            self.__build_detail_columns(detail_rows),
        ]

    def __build_list_controls(self) -> list[ft.Control]:
        filtered_items = self.__get_filtered_items()
        if not filtered_items:
            return [ft.Text(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]

        controls: list[ft.Control] = []
        for item_schema in filtered_items:
            controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(item_schema.name),
                        subtitle=ft.Text(
                            f"{self._translation.get('index')}: {item_schema.index} | "
                            f"{self._translation.get('category')}: {item_schema.category_name}"
                        ),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=self.__build_item_click_handler(item_schema.id, item_schema.stock_quantity),
                    )
                )
            )
        return controls

    def __get_filtered_items(self) -> list[ItemPlainSchema]:
        items = self.__items
        if self.__selected_category_id is not None:
            items = [item for item in items if item.category_id == self.__selected_category_id]
        if self.__index_filter:
            filter_normalized = self.__index_filter.lower()
            items = [item for item in items if filter_normalized in item.index.lower()]
        return items

    def __on_back_clicked(self, _: ft.ControlEvent) -> None:
        if self.__mode == self.__MODE_LIST:
            self._controller.on_back_to_menu()
            return
        self._controller.on_back_from_details()

    def __on_category_filter_changed(self) -> None:
        self.__selected_category_id = self.__parse_optional_int(self.__category_filter_input.value)
        self.__items_list.controls = self.__build_list_controls()
        self.__update_if_attached()

    def __on_index_filter_changed(self, _: ft.ControlEvent) -> None:
        self.__index_filter = (self.__index_filter_input.value or "").strip()
        self.__items_list.controls = self.__build_list_controls()
        self.__update_if_attached()

    def __build_item_click_handler(self, item_id: int, quantity: int):
        return lambda _: self._controller.on_item_selected(
            item_id,
            quantity,
            self.__selected_category_id,
            self.__index_filter,
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
            return ft.Container(
                content=ft.Text(self._translation.get("no_images"), text_align=ft.TextAlign.CENTER),
                padding=ft.Padding.symmetric(vertical=8),
            )

        thumbnails_row = ft.Row(spacing=8, run_spacing=8, alignment=ft.MainAxisAlignment.CENTER)

        def update_buttons() -> None:
            left_button.disabled = self.__gallery_start_index <= 0
            right_button.disabled = self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE >= len(image_urls)
            self.__safe_update(left_button)
            self.__safe_update(right_button)

        def render_thumbnails() -> None:
            thumbnails_row.controls.clear()
            window = image_urls[self.__gallery_start_index : self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE]
            for url in window:
                thumbnails_row.controls.append(
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
            self.__safe_update(thumbnails_row)
            update_buttons()

        def move_left(_: ft.ControlEvent) -> None:
            if self.__gallery_start_index <= 0:
                return
            self.__gallery_start_index -= 1
            render_thumbnails()

        def move_right(_: ft.ControlEvent) -> None:
            if self.__gallery_start_index + self.__GALLERY_WINDOW_SIZE >= len(image_urls):
                return
            self.__gallery_start_index += 1
            render_thumbnails()

        left_button = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=move_left, disabled=True)
        right_button = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=move_right, disabled=True)
        render_thumbnails()
        return ft.Row(
            controls=[left_button, ft.Container(content=thumbnails_row, expand=True), right_button],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

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
        self._controller._queue_dialog(dialog)

    def __close_dialog(self) -> None:
        try:
            self.page.pop_dialog()
        except RuntimeError:
            return

    def __image_urls(self) -> list[str]:
        if not self.__item:
            return []
        ordered_images = sorted(self.__item.images, key=lambda image: image.order)
        return [image.url for image in ordered_images if image.url]

    def __build_detail_rows(self) -> list[tuple[str, str]]:
        if not self.__item:
            return []
        data = self.__item.model_dump()
        data["quantity"] = self.__quantity
        rows: list[tuple[str, str]] = []
        used_keys: set[str] = set()

        for key in self.__DETAIL_FIELDS_ORDER:
            if key not in data or self.__is_excluded_field(key):
                continue
            rows.append((self.__label_for_key(key), self.__format_value(data[key])))
            used_keys.add(key)

        for key, value in data.items():
            if key in used_keys or self.__is_excluded_field(key):
                continue
            rows.append((self.__label_for_key(key), self.__format_value(value)))

        return rows

    def __is_excluded_field(self, key: str) -> bool:
        return (
            key == "images"
            or key in self.__META_FIELDS
            or key in self.__FINANCIAL_FIELDS
            or key in self.__BIN_AND_DISCOUNT_FIELDS
        )

    def __label_for_key(self, key: str) -> str:
        label_overrides = {
            "quantity": self._translation.get("quantity"),
            "category_name": self._translation.get("category"),
        }
        if key in label_overrides:
            return label_overrides[key]
        return self._translation.get(key)

    def __format_value(self, value: Any) -> str:
        if value is None:
            return "-"
        if isinstance(value, bool):
            return self._translation.get("yes") if value else self._translation.get("no")
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, list):
            if not value:
                return "-"
            return ", ".join(str(item) for item in value)
        if isinstance(value, float):
            return f"{value:g}"
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
            width=140,
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
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        )

    def __update_if_attached(self) -> None:
        try:
            self.update()
        except RuntimeError:
            return

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
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
