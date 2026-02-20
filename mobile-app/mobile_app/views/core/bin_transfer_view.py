from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import BinTransferViewStyles, ButtonStyles, MobileCommonViewStyles, TypographyStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.bin_transfer_controller import BinTransferController


class BinTransferView(BaseView):
    def __init__(
        self,
        controller: BinTransferController,
        translation: Translation,
        view_key: View,
    ) -> None:
        super().__init__(controller, translation, view_key)

        self.__source_items: list[tuple[int, str, int]] = []
        self.__pending_items: list[tuple[int, str, int]] = []
        self.__last_quantity_item_id: int | None = None
        self.__form_enabled = False

        self.__title = self._get_label("", style=TypographyStyles.HEADER_TITLE)
        self.__back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_back_click,
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

        self.__source_input = self._get_text_field(
            value="",
            on_change=lambda event: self._controller.on_value_changed("source_bin"),
            on_submit=lambda event: self._controller.on_value_changed("source_bin", self.__on_source_submit),
            on_focus=lambda event: self._controller.on_value_changed("source_bin", self.__on_source_submit)
            if str(getattr(event, "data", "")).lower() == "false"
            else None,
            on_tap_outside=lambda event: self._controller.on_value_changed("source_bin", self.__on_source_submit
            ),
            expand=True,
        )
        self.__source_input.col = BinTransferViewStyles.SOURCE_BIN_COL

        self.__target_input = self._get_text_field(
            value="",
            on_change=lambda event: self._controller.on_value_changed("target_bin"),
            on_submit=lambda event: self._controller.on_value_changed("target_bin", self.__on_target_submit),
            on_focus=lambda event: self._controller.on_value_changed("target_bin", self.__on_target_submit)
            if str(getattr(event, "data", "")).lower() == "false"
            else None,
            on_tap_outside=lambda event: self._controller.on_value_changed("target_bin", self.__on_target_submit
            ),
            expand=True,
        )
        self.__target_input.col = BinTransferViewStyles.TARGET_BIN_COL

        self.__item_input = self._get_dropdown(
            options=[],
            include_empty_option=True,
            on_select=lambda event: self._controller.on_value_changed("item_id", self.__on_item_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__item_input.col = BinTransferViewStyles.ITEM_COL
        self.__item_input.disabled = True
        self.__item_input.value = "0"

        self.__quantity_input = self._get_numeric_field(
            value=1,
            step=1,
            precision=0,
            min_value=1,
            is_float=False,
            on_change=lambda event: self._controller.on_value_changed("quantity"),
            expand=True,
        )
        self.__available_text = self._get_label("", size=BinTransferViewStyles.AVAILABLE_TEXT_SIZE)
        quantity_info_container = ft.Container(
            col=BinTransferViewStyles.QUANTITY_INFO_COL,
            alignment=BinTransferViewStyles.QUANTITY_INFO_ALIGNMENT,
            content=ft.Column(
                controls=[
                    self.__quantity_input,
                    ft.Container(
                        content=self.__available_text,
                        alignment=BinTransferViewStyles.QUANTITY_INFO_TEXT_CONTAINER_ALIGNMENT,
                        expand=True,
                    ),
                ],
                spacing=BinTransferViewStyles.QUANTITY_INFO_COLUMN_SPACING,
                tight=True,
                horizontal_alignment=BinTransferViewStyles.QUANTITY_INFO_COLUMN_HORIZONTAL_ALIGNMENT,
            ),
        )

        self.__add_button = self._get_button(on_click=self.__on_add_click, disabled=True)
        self.__save_button = self._get_button(on_click=self.__on_save_click, disabled=True)
        add_button_container = ft.Container(
            col=BinTransferViewStyles.ADD_BUTTON_COL,
            alignment=BinTransferViewStyles.QUANTITY_INFO_ALIGNMENT,
            content=self.__add_button,
        )

        self.__pending_title = self._get_label("", style=TypographyStyles.PENDING_TITLE)
        self.__pending_header_row = ft.Row(
            controls=[self.__pending_title, self.__save_button],
            alignment=BinTransferViewStyles.PENDING_HEADER_ALIGNMENT,
            vertical_alignment=BinTransferViewStyles.PENDING_HEADER_VERTICAL_ALIGNMENT,
        )
        self.__pending_list = ft.Column(spacing=BinTransferViewStyles.PENDING_ROW_SPACING)
        self.__pending_section = ft.Column(
            controls=[self.__pending_header_row, self.__pending_list],
            spacing=BinTransferViewStyles.PENDING_ROW_SPACING,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self._add_to_inputs(
            {
                "source_bin": self.__source_input,
                "target_bin": self.__target_input,
                "item_id": self.__item_input,
                "quantity": self.__quantity_input,
            }
        )

        self.__bins_row = ft.ResponsiveRow(
            controls=[self.__source_input, self.__target_input],
            columns=BinTransferViewStyles.BINS_ROW_COLUMNS,
            alignment=BinTransferViewStyles.BINS_ROW_ALIGNMENT,
            vertical_alignment=BinTransferViewStyles.BINS_ROW_VERTICAL_ALIGNMENT,
        )
        self.__form_row = ft.ResponsiveRow(
            controls=[self.__item_input, quantity_info_container, add_button_container],
            columns=BinTransferViewStyles.FORM_ROW_COLUMNS,
            alignment=BinTransferViewStyles.FORM_ROW_ALIGNMENT,
            vertical_alignment=BinTransferViewStyles.FORM_ROW_VERTICAL_ALIGNMENT,
        )

        self._master_column.controls = [
            self.__header_row,
            self.__bins_row,
            self.__form_row,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__pending_section,
        ]
        self.__render_static_texts()
        self.__render_pending_list()

    def did_mount(self) -> None:
        try:
            self.__quantity_input.read_only = False
        except RuntimeError:
            pass
        super().did_mount()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.__render_source_item_options()
        self.__render_pending_list()
        self.__update_available_text()
        self.safe_update(self)

    def set_source_error(self, message: str | None) -> None:
        self.__source_input.error = message
        self.safe_update(self.__source_input)

    def set_target_error(self, message: str | None) -> None:
        self.__target_input.error = message
        self.safe_update(self.__target_input)

    def set_source_items(self, items: list[tuple[int, str, int]]) -> None:
        self.__source_items = items
        self.__render_source_item_options()
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()
        self.safe_update(self.__item_input)
        self.safe_update(self.__available_text)

    def set_pending_items(self, items: list[tuple[int, str, int]]) -> None:
        self.__pending_items = items
        self.__render_pending_list()
        self.safe_update(self.__pending_section)

    def set_form_enabled(self, enabled: bool) -> None:
        self.__form_enabled = enabled
        self.__item_input.disabled = not enabled
        self.__quantity_input.read_only = not enabled
        self.__sync_quantity_limit_to_selected_item()
        self.__update_add_button_state()
        self.safe_update(self.__item_input)
        self.safe_update(self.__quantity_input)
        self.safe_update(self.__add_button)

    def set_save_enabled(self, enabled: bool) -> None:
        self.__save_button.disabled = not enabled
        self.safe_update(self.__save_button)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("bin_transfer")
        self.__source_input.label = self._translation.get("source_bin")
        self.__target_input.label = self._translation.get("target_bin")
        self.__item_input.label = self._translation.get("item")
        self.__add_button.content = self._translation.get("add")
        self.__save_button.content = self._translation.get("save")
        self.__back_button.content = self._translation.get("back")
        self.__pending_title.value = self._translation.get("pending_transfers")
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()

    def __render_source_item_options(self) -> None:
        self.__item_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(item_id), text=self.__build_item_option_label(item_index))
            for item_id, item_index, _available_quantity in self.__source_items
        ]
        self.__item_input.value = "0"
        self.__item_input.error_text = None

    def __render_pending_list(self) -> None:
        if not self.__pending_items:
            self.__pending_list.controls = [
                self._get_label(self._translation.get("no_pending_transfers"), text_align=ft.TextAlign.CENTER)
            ]
            return
        rows: list[ft.Control] = []
        for item_id, item_index, quantity in self.__pending_items:
            rows.append(
                ft.Card(
                    bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                    content=ft.ListTile(
                        title=self._get_label(item_index),
                        subtitle=self._get_label(f"{self._translation.get('quantity')}: {quantity}"),
                        trailing=self._get_icon_button(
                            icon=ft.Icons.CLOSE,
                            on_click=self.__build_remove_handler(item_id),
                        ),
                    )
                )
            )
        self.__pending_list.controls = rows

    def __build_item_option_label(self, item_index: str) -> str:
        return item_index

    def __on_source_submit(self) -> None:
        self._controller.on_source_bin_submit(self.__source_input.value or "")

    def __on_target_submit(self) -> None:
        self._controller.on_target_bin_submit(self.__target_input.value or "")

    def __on_add_click(self, _: ft.Event[ft.Button]) -> None:
        item_id = self.__parse_optional_int(self.__item_input.value)
        quantity = self.__parse_quantity(self.__quantity_input.value)
        self._controller.on_add_clicked(item_id, quantity)

    def __on_save_click(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_save_clicked()

    def __on_back_click(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_back_to_menu()

    def __on_item_changed(self) -> None:
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()
        self.__update_add_button_state()
        self.safe_update(self.__available_text)
        self.safe_update(self.__add_button)

    def __build_remove_handler(self, item_id: int):
        return lambda _: self._controller.on_pending_item_removed(item_id)

    @staticmethod
    def __parse_optional_int(value: str | None) -> int | None:
        if not value:
            return None
        stripped = value.strip()
        if stripped in {"", "0"}:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None

    @staticmethod
    def __parse_quantity(value: int | float | None) -> int | None:
        if value is None:
            return None
        parsed = int(value)
        if parsed <= 0:
            return None
        return parsed

    def __update_available_text(self) -> None:
        selected_item_id = self.__parse_optional_int(self.__item_input.value)
        if selected_item_id is None:
            self.__available_text.value = f"{self._translation.get('available')}: -"
            return
        available_quantity = 0
        for item_id, _, quantity in self.__source_items:
            if item_id == selected_item_id:
                available_quantity = quantity
                break
        self.__available_text.value = f"{self._translation.get('available')}: {available_quantity}"
        self.__available_text.text_align = BinTransferViewStyles.QUANTITY_INFO_TEXT_ALIGN

    def __sync_quantity_limit_to_selected_item(self) -> None:
        selected_item_id = self.__parse_optional_int(self.__item_input.value)
        previous_item_id = self.__last_quantity_item_id
        max_quantity = 0
        if selected_item_id is not None:
            for item_id, _, quantity in self.__source_items:
                if item_id == selected_item_id:
                    max_quantity = max(1, quantity)
                    break
        current_value = self.__parse_quantity(self.__quantity_input.value) or 0
        should_use_available_default = (
            selected_item_id is None or selected_item_id != previous_item_id or current_value > max_quantity
        )
        if should_use_available_default:
            normalized_value = max_quantity
        else:
            normalized_value = max(0, min(current_value, max_quantity))
        try:
            self.__quantity_input.set_limits(0, max_quantity)
            self.__quantity_input.value = normalized_value
            self.__last_quantity_item_id = selected_item_id
        except RuntimeError:
            return

    def __update_add_button_state(self) -> None:
        selected_item_id = self.__parse_optional_int(self.__item_input.value)
        self.__add_button.disabled = (not self.__form_enabled) or selected_item_id is None
