from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import flet as ft

from schemas.business.logistic.item_schema import ItemPlainSchema
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.mobile.items_controller import ItemsController


class ItemsView(BaseView):
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
    ) -> None:
        super().__init__(controller, translation, mode, view_key, data_row, 0, 0)
        self.__item = item
        self.__quantity = quantity
        self.__gallery_start_index = 0

        self.__title = ft.Text(size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.__subtitle = ft.Text(size=14, text_align=ft.TextAlign.CENTER)
        self.__details = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=8)
        self.__back_button = ft.Button(on_click=self.__on_back_clicked, width=220)

        self._master_column.controls = [
            self.__title,
            self.__subtitle,
            ft.Divider(height=1),
            self.__details,
            ft.Container(height=8),
            ft.Row(
                controls=[self.__back_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
        self.__render()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render()
        self.__update_if_attached()

    def __render(self) -> None:
        self.__title.value = self._translation.get("item_details")
        self.__back_button.content = self._translation.get("back_to_items")
        if not self.__item:
            self.__subtitle.value = self._translation.get("no_items")
            self.__details.controls = [ft.Text(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]
            return

        self.__subtitle.value = self.__item.name
        image_urls = self.__resolve_image_urls()
        max_start_index = max(0, len(image_urls) - self.__GALLERY_WINDOW_SIZE)
        self.__gallery_start_index = min(self.__gallery_start_index, max_start_index)
        detail_rows = self.__build_detail_rows()
        self.__details.controls = [
            self.__build_gallery_section(image_urls),
            ft.Divider(height=1),
            self.__build_detail_columns(detail_rows),
        ]

    def __on_back_clicked(self, _: ft.ControlEvent) -> None:
        self._controller.on_back_to_bins()

    def __build_gallery_section(self, image_urls: list[str]) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text(self.__resolve_label("images"), weight=ft.FontWeight.W_600),
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

    def __resolve_image_urls(self) -> list[str]:
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
            rows.append((self.__resolve_label(key), self.__format_value(data[key])))
            used_keys.add(key)

        for key, value in data.items():
            if key in used_keys or self.__is_excluded_field(key):
                continue
            rows.append((self.__resolve_label(key), self.__format_value(value)))

        return rows

    def __is_excluded_field(self, key: str) -> bool:
        return (
            key == "images"
            or key in self.__META_FIELDS
            or key in self.__FINANCIAL_FIELDS
            or key in self.__BIN_AND_DISCOUNT_FIELDS
        )

    def __resolve_label(self, key: str) -> str:
        label_overrides = {
            "quantity": self._translation.get("quantity"),
            "category_name": self._translation.get("category"),
        }
        if key in label_overrides:
            return label_overrides[key]
        translated = self._translation.get(key)
        if translated != key:
            return translated
        return key.replace("_", " ").capitalize()

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
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
