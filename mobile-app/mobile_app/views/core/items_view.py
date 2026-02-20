from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import flet as ft
from styles.styles import AlignmentStyles, ButtonStyles, ItemsViewStyles, MobileCommonViewStyles, TypographyStyles
from schemas.business.logistic.item_schema import ItemPlainSchema
from utils.enums import View
from utils.translation import Translation
from views.base.base_dialog import BaseDialog
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.items_controller import ItemsController


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
    def __init__(
        self,
        controller: ItemsController,
        translation: Translation,
        view_key: View,
        item: ItemPlainSchema | None,
        quantity: int,
        items: list[ItemPlainSchema],
        categories: list[tuple[int, str]],
        selected_category_id: int | None,
        index_filter: str,
        caller_view_key: View | None,
    ) -> None:
        super().__init__(controller, translation, view_key, caller_view_key=caller_view_key)
        self.__item = item
        self.__quantity = quantity
        self.__items = items
        self.__categories = categories
        self.__selected_category_id = selected_category_id
        self.__index_filter = index_filter.strip()
        self.__gallery_start_index = 0
        self.__gallery_image_urls: list[str] = []
        self.__gallery_thumbnails_row: ft.Row | None = None
        self.__gallery_left_button: ft.IconButton | None = None
        self.__gallery_right_button: ft.IconButton | None = None

        self.__title = self._get_label("", style=TypographyStyles.HEADER_TITLE)
        self.__back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_back_clicked,
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

        self.__category_filter_input = self._get_dropdown(
            options=self.__categories,
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("category_filter", self.__on_category_filter_changed
            ),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__category_filter_input.col = self._responsive_col(ItemsViewStyles.CATEGORY_FILTER_INPUT_SIZE)
        self.__category_filter_input.options = [
            ft.dropdown.Option(key="0", text=self._translation.get("all_categories")),
            *[ft.dropdown.Option(key=str(category_id), text=name) for category_id, name in self.__categories],
        ]
        self.__category_filter_input.value = str(self.__selected_category_id) if self.__selected_category_id else "0"

        self.__index_filter_input = self._get_text_field(
            value="",
            on_change=lambda event: self._controller.on_value_changed("index_filter"),
            on_submit=lambda event: self._controller.on_value_changed("index_filter"),
            on_focus=lambda event: self._controller.on_value_changed("index_filter")
            if str(getattr(event, "data", "")).lower() == "false"
            else None,
            on_tap_outside=lambda event: self._controller.on_value_changed("index_filter"),
            expand=True,
        )
        self.__index_filter_input.col = self._responsive_col(ItemsViewStyles.INDEX_FILTER_INPUT_SIZE)
        self.__index_filter_input.value = self.__index_filter
        self.__index_filter_input.on_change = self.__on_index_filter_changed
        self.__index_filter_input.dense = True
        self.__index_filter_input.prefix_icon = ft.Icons.SEARCH

        self._add_to_inputs(
            {
                "category_filter": self.__category_filter_input,
                "index_filter": self.__index_filter_input,
            }
        )

        self.__filters_row = ft.ResponsiveRow(
            controls=[self.__category_filter_input, self.__index_filter_input],
            columns=ItemsViewStyles.FILTER_ROW_COLUMNS,
            alignment=ItemsViewStyles.FILTER_ROW_ALIGNMENT,
            vertical_alignment=ItemsViewStyles.FILTER_ROW_VERTICAL_ALIGNMENT,
        )
        self.__items_list = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=MobileCommonViewStyles.LIST_SPACING)
        self.__list_section = ft.Column(
            controls=[self.__filters_row, ft.Divider(height=ItemsViewStyles.DETAILS_DIVIDER_HEIGHT), self.__items_list],
            spacing=MobileCommonViewStyles.SECTION_SPACING,
            expand=True,
        )

        self.__details = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=MobileCommonViewStyles.SECTION_SPACING)
        self.__details_section = ft.Column(
            controls=[self.__details],
            spacing=ItemsViewStyles.DETAILS_SECTION_SPACING,
            expand=True,
        )

        self._master_column.controls = [
            self.__header_row,
            ft.Divider(height=ItemsViewStyles.DETAILS_DIVIDER_HEIGHT),
            self.__list_section,
            self.__details_section,
        ]
        self.__render()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render()
        self.safe_update(self)

    def __render(self) -> None:
        if self.__item is None:
            self.__render_list_mode()
            return
        self.__render_details_mode()

    def __render_list_mode(self) -> None:
        self.__title.value = self._translation.get("items")
        self.__back_button.content = self._translation.get("back")
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
        self.__back_button.content = self._translation.get("back")
        self.__list_section.visible = False
        self.__details_section.visible = True

        if not self.__item:
            self.__details.controls = [self._get_label(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]
            return

        image_urls = self.__image_urls()
        max_start_index = max(0, len(image_urls) - ItemsViewStyles.GALLERY_WINDOW_SIZE)
        self.__gallery_start_index = min(self.__gallery_start_index, max_start_index)
        detail_rows = self.__build_detail_rows()
        self.__details.controls = [
            self.__build_gallery_section(image_urls),
            ft.Divider(height=ItemsViewStyles.DETAILS_DIVIDER_HEIGHT),
            self.__build_detail_columns(detail_rows),
        ]

    def __build_list_controls(self) -> list[ft.Control]:
        filtered_items = self.__get_filtered_items()
        if not filtered_items:
            return [self._get_label(self._translation.get("no_items"), text_align=ft.TextAlign.CENTER)]

        controls: list[ft.Control] = []
        for item_schema in filtered_items:
            controls.append(
                ft.Card(
                    bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                    content=ft.ListTile(
                        title=self._get_label(item_schema.name),
                        subtitle=self._get_label(
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

    def __on_back_clicked(self, _: ft.Event[ft.Button]) -> None:
        if self.__item is None:
            self._controller.on_back_to_menu()
            return
        self._controller.on_back_from_details()

    def __on_category_filter_changed(self) -> None:
        self.__selected_category_id = self.__parse_optional_int(self.__category_filter_input.value)
        self.__items_list.controls = self.__build_list_controls()
        self.safe_update(self)

    def __on_index_filter_changed(self, _: ft.Event[ft.TextField]) -> None:
        self.__index_filter = (self.__index_filter_input.value or "").strip()
        self.__items_list.controls = self.__build_list_controls()
        self.safe_update(self)

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
                self._get_label(self._translation.get("images"), style=TypographyStyles.SECTION_TITLE),
                self.__build_gallery_control(image_urls),
            ],
            tight=True,
            spacing=ItemsViewStyles.GALLERY_SECTION_SPACING,
        )

    def __build_gallery_control(self, image_urls: list[str]) -> ft.Control:
        if not image_urls:
            self.__gallery_image_urls = []
            self.__gallery_thumbnails_row = None
            self.__gallery_left_button = None
            self.__gallery_right_button = None
            return ft.Container(
                content=self._get_label(self._translation.get("no_images"), text_align=ft.TextAlign.CENTER),
                padding=ItemsViewStyles.GALLERY_EMPTY_PADDING,
            )
        self.__gallery_image_urls = list(image_urls)
        self.__gallery_thumbnails_row = ft.Row(
            spacing=ItemsViewStyles.GALLERY_THUMB_ROW_SPACING,
            run_spacing=ItemsViewStyles.GALLERY_THUMB_ROW_RUN_SPACING,
            alignment=ItemsViewStyles.GALLERY_THUMB_ROW_ALIGNMENT,
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
            spacing=ItemsViewStyles.GALLERY_CONTROL_SPACING,
            vertical_alignment=ItemsViewStyles.GALLERY_ROW_VERTICAL_ALIGNMENT,
        )

    def __move_gallery_left(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index <= 0:
            return
        self.__gallery_start_index -= 1
        self.__render_gallery_thumbnails()

    def __move_gallery_right(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__gallery_start_index + ItemsViewStyles.GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls):
            return
        self.__gallery_start_index += 1
        self.__render_gallery_thumbnails()

    def __render_gallery_thumbnails(self) -> None:
        if self.__gallery_thumbnails_row is None:
            return
        self.__gallery_thumbnails_row.controls.clear()
        window = self.__gallery_image_urls[
            self.__gallery_start_index : self.__gallery_start_index + ItemsViewStyles.GALLERY_WINDOW_SIZE
        ]
        for url in window:
            self.__gallery_thumbnails_row.controls.append(
                ft.Container(
                    expand=1,
                    alignment=AlignmentStyles.CENTER,
                    content=ft.Image(
                        src=url,
                        expand=True,
                        fit=ft.BoxFit.CONTAIN,
                        aspect_ratio=ItemsViewStyles.GALLERY_THUMB_ASPECT_RATIO,
                    ),
                    on_click=lambda _, image_url=url: self.__open_image_dialog(image_url),
                )
            )
        missing_slots = max(0, ItemsViewStyles.GALLERY_WINDOW_SIZE - len(window))
        for _ in range(missing_slots):
            self.__gallery_thumbnails_row.controls.append(ft.Container(expand=1))
        self.safe_update(self.__gallery_thumbnails_row)
        self.__update_gallery_buttons()

    def __update_gallery_buttons(self) -> None:
        if self.__gallery_left_button is None or self.__gallery_right_button is None:
            return
        self.__gallery_left_button.disabled = self.__gallery_start_index <= 0
        self.__gallery_right_button.disabled = (
            self.__gallery_start_index + ItemsViewStyles.GALLERY_WINDOW_SIZE >= len(self.__gallery_image_urls)
        )
        self.safe_update(self.__gallery_left_button)
        self.safe_update(self.__gallery_right_button)

    def __open_image_dialog(self, url: str) -> None:
        dialog = BaseDialog(
            title=None,
            controls=[
                ft.Container(
                    width=ItemsViewStyles.GALLERY_DIALOG_IMAGE_WIDTH,
                    height=ItemsViewStyles.GALLERY_DIALOG_IMAGE_HEIGHT,
                    content=ft.Image(
                        src=url,
                        width=ItemsViewStyles.GALLERY_DIALOG_IMAGE_WIDTH,
                        height=ItemsViewStyles.GALLERY_DIALOG_IMAGE_HEIGHT,
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
        )

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
        rows: list[ft.Control] = [
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col=ItemsViewStyles.DETAILS_LABEL_COL,
                        padding=ItemsViewStyles.DETAILS_LABEL_PADDING,
                        content=self._get_label(
                            f"{self._translation.get(label)}:",
                            style=TypographyStyles.DETAIL_LABEL,
                        ),
                    ),
                    ft.Container(
                        col=ItemsViewStyles.DETAILS_VALUE_COL,
                        padding=ItemsViewStyles.DETAILS_VALUE_PADDING,
                        content=self._get_label(value, selectable=True),
                    ),
                ],
                columns=ItemsViewStyles.DETAILS_PAIR_COLUMNS,
                alignment=AlignmentStyles.AXIS_START,
                vertical_alignment=ItemsViewStyles.DETAIL_ROW_VERTICAL_ALIGNMENT,
            )
            for label, value in detail_rows
        ]
        return ft.Container(
            padding=ItemsViewStyles.DETAILS_WRAPPER_PADDING,
            content=ft.Column(
                controls=rows,
                spacing=ItemsViewStyles.DETAILS_COL_SPACING,
                tight=True,
            ),
        )

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
