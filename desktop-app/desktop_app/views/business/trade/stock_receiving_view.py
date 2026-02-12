from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast

import flet as ft
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_desktop_view import BaseDesktopView
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from controllers.business.trade.stock_receiving_controller import StockReceivingController


class StockReceivingView(BaseDesktopView):
    def __init__(
        self,
        controller: StockReceivingController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        orders: list[tuple[int, str]],
        on_target_submitted: Callable[[ft.Event[ft.TextField]], None],
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        on_move_requested: Callable[[list[int]], None],
        on_pending_reverted: Callable[[list[int]], None],
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None

        order_container, _ = self._get_dropdown("order_id", 12, orders, callbacks=[self.__handle_order_changed])
        self.__order_input = cast(ft.Dropdown, order_container.content)
        self.__order_input.label = self._translation.get("order")
        order_container.expand = True
        target_container, _ = self._get_text_input("target_bin", 12)
        self.__target_input = cast(ft.TextField, target_container.content)
        self.__target_input.label = self._translation.get("target_bin")
        self.__target_input.on_submit = on_target_submitted
        target_container.expand = True
        self._add_to_inputs(
            {
                "order_id": FieldGroup(
                    label=self._get_label("order", 0, colon=False),
                    input=(order_container, 12),
                    marker=self._get_marker("order_id", 0),
                ),
                "target_bin": FieldGroup(
                    label=self._get_label("target_bin", 0, colon=False),
                    input=(target_container, 12),
                    marker=self._get_marker("target_bin", 0),
                ),
            }
        )

        self.__bulk_transfer = BulkTransfer(
            on_save_clicked=on_save_clicked,
            source_label=self._translation.get("order_items"),
            target_label=self._translation.get("target_bin"),
            on_move_requested=on_move_requested,
            on_pending_reverted=on_pending_reverted,
            source_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("quantity"),
            ],
            target_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("quantity"),
            ],
        )
        self.__bulk_transfer.set_enabled_states(False, False, False)

        inputs_row = ft.Row(
            controls=[
                order_container,
                ft.Container(expand=True),
                target_container,
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self._master_column.controls = [inputs_row, self.__bulk_transfer]
        self.content = ft.Container(content=self._master_column, expand=True)

    def set_orders(self, orders: list[tuple[int, str]]) -> None:
        self.__order_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(order_id), text=label) for order_id, label in orders
        ]
        if self.__order_input.page:
            self.__order_input.update()

    def set_order_error(self, message: str | None) -> None:
        self.__order_input.error_text = message
        if self.__order_input.page:
            self.__order_input.update()

    def set_target_error(self, message: str | None) -> None:
        self.__target_input.error = message
        if self.__target_input.page:
            self.__target_input.update()

    def set_source_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_source_rows(rows)

    def set_target_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_target_rows(rows)

    def mark_source_items_as_moved(self, ids: list[int]) -> None:
        self.__bulk_transfer.mark_source_items_as_moved(ids)

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return self.__bulk_transfer.get_pending_targets()

    def add_target_row(self, source_id: int, values: list[str]) -> int:
        return self.__bulk_transfer.add_target_row(source_id, values, highlight=True)

    def update_existing_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        self.__bulk_transfer.update_existing_target(target_id, source_id, values)

    def set_source_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_source_enabled(enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_target_enabled(enabled)

    def __handle_order_changed(self) -> None:
        self._controller.on_order_changed(self.__order_input.value)
