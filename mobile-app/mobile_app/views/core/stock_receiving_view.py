from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import ButtonStyles, MobileCommonViewStyles, StockReceivingViewStyles, TypographyStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.stock_receiving_controller import StockReceivingController


class StockReceivingView(BaseView):
    def __init__(
        self,
        controller: StockReceivingController,
        translation: Translation,
        view_key: View,
        orders: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, view_key)

        self.__source_rows: list[tuple[int, str, str, int]] = []
        self.__moved_source_ids: set[int] = set()
        self.__pending_rows: dict[int, tuple[int, str, str, int]] = {}
        self.__saved_rows: list[tuple[int, str, str, int]] = []
        self.__next_temp_target_id = -1

        self.__source_enabled = False
        self.__target_enabled = False
        self.__last_quantity_item_id: int | None = None

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

        self.__order_input = self._get_dropdown(
            options=orders,
            include_empty_option=True,
            on_select=lambda _: self._controller.on_value_changed("order_id", self.__on_order_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__order_input.col = StockReceivingViewStyles.ORDER_COL
        self.__order_input.value = "0"

        self.__target_input = self._get_text_field(
            value="",
            on_change=lambda _: self._controller.on_value_changed("target_bin"),
            on_submit=lambda _: self._controller.on_value_changed("target_bin", self.__on_target_submit),
            on_focus=lambda event: (
                self._controller.on_value_changed("target_bin", self.__on_target_submit)
                if str(getattr(event, "data", "")).lower() == "false"
                else None
            ),
            on_tap_outside=lambda _: self._controller.on_value_changed("target_bin", self.__on_target_submit),
            expand=True,
        )
        self.__target_input.col = StockReceivingViewStyles.TARGET_BIN_COL

        self.__item_input = self._get_dropdown(
            options=[],
            include_empty_option=True,
            on_select=lambda _: self._controller.on_value_changed("item_id", self.__on_item_changed),
            value="0",
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__item_input.col = StockReceivingViewStyles.ITEM_COL
        self.__item_input.value = "0"
        self.__item_input.disabled = True

        self.__quantity_input = self._get_numeric_field(
            value=0,
            step=1,
            precision=0,
            min_value=0,
            is_float=False,
            on_change=lambda _: self._controller.on_value_changed("quantity"),
            expand=True,
        )

        self.__available_text = self._get_label(
            "",
            size=StockReceivingViewStyles.AVAILABLE_TEXT_SIZE,
            text_align=StockReceivingViewStyles.QUANTITY_INFO_TEXT_ALIGN,
        )
        quantity_info_container = ft.Container(
            col=StockReceivingViewStyles.QUANTITY_INFO_COL,
            alignment=StockReceivingViewStyles.QUANTITY_INFO_ALIGNMENT,
            content=ft.Column(
                controls=[
                    self.__quantity_input,
                    ft.Container(
                        content=self.__available_text,
                        alignment=StockReceivingViewStyles.QUANTITY_INFO_TEXT_CONTAINER_ALIGNMENT,
                        expand=True,
                    ),
                ],
                spacing=StockReceivingViewStyles.QUANTITY_INFO_COLUMN_SPACING,
                tight=True,
                horizontal_alignment=StockReceivingViewStyles.QUANTITY_INFO_COLUMN_HORIZONTAL_ALIGNMENT,
            ),
        )

        self.__add_button = self._get_button(on_click=self.__on_add_clicked, disabled=True)
        add_button_container = ft.Container(
            col=StockReceivingViewStyles.ADD_BUTTON_COL,
            alignment=StockReceivingViewStyles.QUANTITY_INFO_ALIGNMENT,
            content=self.__add_button,
        )

        self.__save_button = self._get_button(on_click=self.__on_save_clicked, disabled=True)
        self.__pending_title = self._get_label("", style=TypographyStyles.PENDING_TITLE)
        self.__pending_header_row = ft.Row(
            controls=[self.__pending_title, self.__save_button],
            alignment=StockReceivingViewStyles.PENDING_HEADER_ALIGNMENT,
            vertical_alignment=StockReceivingViewStyles.PENDING_HEADER_VERTICAL_ALIGNMENT,
        )
        self.__pending_list = ft.Column(spacing=StockReceivingViewStyles.PENDING_ROW_SPACING)
        self.__pending_section = ft.Column(
            controls=[self.__pending_header_row, self.__pending_list],
            spacing=StockReceivingViewStyles.PENDING_SECTION_SPACING,
            scroll=ft.ScrollMode.AUTO,
        )
        self.__saved_title = self._get_label("", style=TypographyStyles.PENDING_TITLE)
        self.__saved_list = ft.Column(spacing=StockReceivingViewStyles.PENDING_ROW_SPACING)
        self.__saved_section = ft.Column(
            controls=[self.__saved_title, self.__saved_list],
            spacing=StockReceivingViewStyles.PENDING_SECTION_SPACING,
            scroll=ft.ScrollMode.AUTO,
        )

        self._add_to_inputs(
            {
                "order_id": self.__order_input,
                "target_bin": self.__target_input,
                "item_id": self.__item_input,
                "quantity": self.__quantity_input,
            }
        )

        self.__top_form_row = ft.ResponsiveRow(
            controls=[self.__order_input, self.__target_input],
            columns=StockReceivingViewStyles.TOP_FORM_ROW_COLUMNS,
            alignment=StockReceivingViewStyles.TOP_FORM_ROW_ALIGNMENT,
            vertical_alignment=StockReceivingViewStyles.TOP_FORM_ROW_VERTICAL_ALIGNMENT,
        )
        self.__pick_form_row = ft.ResponsiveRow(
            controls=[self.__item_input, quantity_info_container, add_button_container],
            columns=StockReceivingViewStyles.PICK_FORM_ROW_COLUMNS,
            alignment=StockReceivingViewStyles.PICK_FORM_ROW_ALIGNMENT,
            vertical_alignment=StockReceivingViewStyles.PICK_FORM_ROW_VERTICAL_ALIGNMENT,
        )

        self._master_column.controls = [
            self.__header_row,
            self.__top_form_row,
            self.__pick_form_row,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__pending_section,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__saved_section,
        ]
        self.__render_static_texts()
        self.__render_source_options()
        self.__render_pending_rows()
        self.__render_saved_rows()
        self.__update_available_text()

    def did_mount(self) -> None:
        try:
            self.__quantity_input.read_only = False
        except RuntimeError:
            pass
        super().did_mount()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.__render_source_options()
        self.__render_pending_rows()
        self.__render_saved_rows()
        self.__update_available_text()
        self.safe_update(self)

    def set_orders(self, orders: list[tuple[int, str]]) -> None:
        self.__order_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(order_id), text=label) for order_id, label in orders
        ]
        self.__order_input.value = "0"
        self.safe_update(self.__order_input)

    def set_order_error(self, message: str | None) -> None:
        self.__order_input.error_text = message
        self.safe_update(self.__order_input)

    def set_target_error(self, message: str | None) -> None:
        self.__target_input.error = message
        self.safe_update(self.__target_input)

    def set_source_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        parsed_rows: list[tuple[int, str, str, int]] = []
        for item_id, values in rows:
            item_index = values[0] if len(values) > 0 else str(item_id)
            item_name = values[1] if len(values) > 1 else ""
            quantity_raw = values[2] if len(values) > 2 else "0"
            quantity = self.__parse_int(quantity_raw, default_value=0)
            parsed_rows.append((item_id, item_index, item_name, max(0, quantity)))
        self.__source_rows = parsed_rows
        self.__moved_source_ids = set()
        self.__render_source_options()
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()
        self.__update_add_button_state()
        self.safe_update(self.__item_input)
        self.safe_update(self.__available_text)
        self.safe_update(self.__add_button)

    def set_target_rows(self, _: list[tuple[int, list[str]]]) -> None:
        self.safe_update(self.__pending_section)

    def set_saved_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        saved_rows: list[tuple[int, str, str, int]] = []
        for item_id, values in rows:
            item_index = values[0] if len(values) > 0 else str(item_id)
            item_name = values[1] if len(values) > 1 else ""
            quantity_raw = values[2] if len(values) > 2 else "0"
            quantity = self.__parse_int(quantity_raw, default_value=0)
            saved_rows.append((item_id, item_index, item_name, max(0, quantity)))
        self.__saved_rows = saved_rows
        self.__render_saved_rows()
        self.safe_update(self.__saved_section)

    def mark_source_items_as_moved(self, ids: list[int]) -> None:
        self.__moved_source_ids = set(ids)
        self.__render_source_options()
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()
        self.__update_add_button_state()
        self.safe_update(self.__item_input)
        self.safe_update(self.__available_text)
        self.safe_update(self.__add_button)

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return [(target_id, row[0]) for target_id, row in self.__pending_rows.items()]

    def add_target_row(self, source_id: int, values: list[str]) -> int:
        item_index = values[0] if len(values) > 0 else str(source_id)
        item_name = values[1] if len(values) > 1 else ""
        quantity_raw = values[2] if len(values) > 2 else "0"
        quantity = self.__parse_int(quantity_raw, default_value=0)
        target_id = self.__next_temp_target_id
        self.__next_temp_target_id -= 1
        self.__pending_rows[target_id] = (source_id, item_index, item_name, max(0, quantity))
        self.__render_pending_rows()
        self.__update_save_button_state()
        self.safe_update(self.__pending_section)
        self.safe_update(self.__save_button)
        return target_id

    def update_existing_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        item_index = values[0] if len(values) > 0 else str(source_id)
        item_name = values[1] if len(values) > 1 else ""
        quantity_raw = values[2] if len(values) > 2 else "0"
        quantity = self.__parse_int(quantity_raw, default_value=0)
        self.__pending_rows[target_id] = (source_id, item_index, item_name, max(0, quantity))
        self.__render_pending_rows()
        self.__update_save_button_state()
        self.safe_update(self.__pending_section)
        self.safe_update(self.__save_button)

    def remove_target_row(self, target_id: int) -> None:
        self.__pending_rows.pop(target_id, None)
        self.__render_pending_rows()
        self.__update_save_button_state()
        self.safe_update(self.__pending_section)
        self.safe_update(self.__save_button)

    def set_source_enabled(self, enabled: bool) -> None:
        self.__source_enabled = enabled
        self.__item_input.disabled = not enabled
        self.__quantity_input.read_only = not enabled
        self.__sync_quantity_limit_to_selected_item()
        self.__update_add_button_state()
        self.safe_update(self.__item_input)
        self.safe_update(self.__quantity_input)
        self.safe_update(self.__add_button)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__target_enabled = enabled
        self.__update_save_button_state()
        self.safe_update(self.__save_button)

    def clear_pending_rows(self) -> None:
        self.__pending_rows.clear()
        self.__render_pending_rows()
        self.__update_save_button_state()
        self.safe_update(self.__pending_section)
        self.safe_update(self.__save_button)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("stock_receiving")
        self.__order_input.label = self._translation.get("tracking_number")
        self.__target_input.label = self._translation.get("target_bin")
        self.__item_input.label = self._translation.get("item")
        self.__add_button.content = self._translation.get("add")
        self.__save_button.content = self._translation.get("save")
        self.__back_button.content = self._translation.get("back")
        self.__pending_title.value = self._translation.get("pending_transfers")
        self.__saved_title.value = self._translation.get("received_items")

    def __render_source_options(self) -> None:
        selectable_rows = [row for row in self.__source_rows if row[0] not in self.__moved_source_ids]
        self.__item_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(item_id), text=self.__build_item_option_text(item_index, item_name))
            for item_id, item_index, item_name, _quantity in selectable_rows
        ]
        self.__item_input.value = "0"
        self.__last_quantity_item_id = None
        self.__item_input.error_text = None

    def __render_pending_rows(self) -> None:
        if not self.__pending_rows:
            self.__pending_list.controls = [
                self._get_label(self._translation.get("no_pending_transfers"), text_align=ft.TextAlign.CENTER),
            ]
            return

        controls: list[ft.Control] = []
        for target_id, (_item_id, item_index, item_name, quantity) in self.__pending_rows.items():
            subtitle = item_name if item_name else "-"
            trailing_control: ft.Control | None = None
            if target_id < 0:
                trailing_control = self._get_icon_button(
                    icon=ft.Icons.CLOSE,
                    on_click=self.__build_pending_remove_handler(target_id),
                )
            controls.append(
                ft.Card(
                    bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                    content=ft.ListTile(
                        title=self._get_label(item_index),
                        subtitle=self._get_label(f"{subtitle} | {self._translation.get('quantity')}: {quantity}"),
                        trailing=trailing_control,
                    ),
                )
            )
        self.__pending_list.controls = controls

    def __render_saved_rows(self) -> None:
        if not self.__saved_rows:
            self.__saved_list.controls = [
                self._get_label(self._translation.get("no_received_items"), text_align=ft.TextAlign.CENTER),
            ]
            return

        controls: list[ft.Control] = []
        for _, item_index, item_name, quantity in self.__saved_rows:
            subtitle = item_name if item_name else "-"
            controls.append(
                ft.Card(
                    bgcolor=MobileCommonViewStyles.LIST_ITEM_BGCOLOR,
                    content=ft.ListTile(
                        title=self._get_label(item_index),
                        subtitle=self._get_label(f"{subtitle} | {self._translation.get('quantity')}: {quantity}"),
                    ),
                )
            )
        self.__saved_list.controls = controls

    def __update_available_text(self) -> None:
        selected_item_id = self._parse_optional_int(self.__item_input.value)
        if selected_item_id is None:
            self.__available_text.value = f"{self._translation.get('available')}: 0"
            return
        available_quantity = 0
        for item_id, _, _, quantity in self.__source_rows:
            if item_id == selected_item_id:
                available_quantity = quantity
                break
        self.__available_text.value = f"{self._translation.get('available')}: {available_quantity}"

    def __sync_quantity_limit_to_selected_item(self) -> None:
        selected_item_id = self._parse_optional_int(self.__item_input.value)
        previous_item_id = self.__last_quantity_item_id
        max_quantity = 0
        if selected_item_id is not None:
            for item_id, _, _, quantity in self.__source_rows:
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
        selected_item_id = self._parse_optional_int(self.__item_input.value)
        self.__add_button.disabled = (not self.__source_enabled) or selected_item_id is None

    def __update_save_button_state(self) -> None:
        self.__save_button.disabled = (not self.__target_enabled) or (not self.__pending_rows)

    def __on_order_changed(self) -> None:
        self._controller.on_order_changed(self.__order_input.value)

    def __on_target_submit(self) -> None:
        self._controller.on_target_bin_submit(self.__target_input.value or "")

    def __on_item_changed(self) -> None:
        self.__sync_quantity_limit_to_selected_item()
        self.__update_available_text()
        self.__update_add_button_state()
        self.safe_update(self.__available_text)
        self.safe_update(self.__add_button)

    def __on_add_clicked(self, _: ft.Event[ft.Button]) -> None:
        item_id = self._parse_optional_int(self.__item_input.value)
        quantity = self.__parse_quantity(self.__quantity_input.value)
        self._controller.on_add_clicked(item_id, quantity)

    def __on_save_clicked(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_save_clicked()

    def __on_back_click(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_back_to_menu()

    def __build_pending_remove_handler(self, target_id: int):
        return lambda _: self.__on_pending_remove(target_id)

    def __on_pending_remove(self, target_id: int) -> None:
        self.__pending_rows.pop(target_id, None)
        self.__render_pending_rows()
        self.__update_save_button_state()
        self.safe_update(self.__pending_section)
        self.safe_update(self.__save_button)
        self._controller.on_pending_item_removed(target_id)

    @staticmethod
    def __build_item_option_text(item_index: str, item_name: str) -> str:
        if item_name:
            return f"{item_index} | {item_name}"
        return item_index

    @staticmethod
    def __parse_quantity(value: int | float | None) -> int | None:
        if value is None:
            return None
        parsed = int(value)
        if parsed <= 0:
            return None
        return parsed

    @staticmethod
    def __parse_int(value: str, default_value: int = 0) -> int:
        try:
            return int(value)
        except ValueError:
            return default_value
