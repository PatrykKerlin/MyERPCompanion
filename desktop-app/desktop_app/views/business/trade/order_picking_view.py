from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast
from datetime import date

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from utils.field_group import FieldGroup
from views.base.base_desktop_view import BaseDesktopView
from views.controls.bulk_transfer_control import BulkTransfer
from views.controls.date_field_control import DateField

if TYPE_CHECKING:
    from controllers.business.trade.order_picking_controller import OrderPickingController


class OrderPickingView(BaseDesktopView):
    def __init__(
        self,
        controller: OrderPickingController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        customers: list[tuple[int, str]],
        default_order_date: date | None,
        orders: list[tuple[int, str]],
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        on_move_requested: Callable[[list[int]], None],
        on_pending_reverted: Callable[[list[int]], None],
        on_package_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        on_package_move_requested: Callable[[list[int]], None],
        on_package_pending_reverted: Callable[[list[int]], None],
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None

        order_date_container, _ = self._get_date_picker(
            "order_date",
            4,
            callbacks=[self.__handle_order_date_changed],
            value=default_order_date,
            read_only=False,
        )
        self.__order_date_input = cast(DateField, order_date_container.content)
        order_date_container.expand = True

        customer_container, _ = self._get_dropdown(
            "customer_id",
            4,
            customers,
            callbacks=[self.__handle_customer_changed],
        )
        self.__customer_input = cast(ft.Dropdown, customer_container.content)
        self.__customer_input.label = self._translation.get("customer")
        self.__customer_input.value = "0"
        customer_container.expand = True

        order_container, _ = self._get_dropdown("order_id", 4, orders, callbacks=[self.__handle_order_changed])
        self.__order_input = cast(ft.Dropdown, order_container.content)
        self.__order_input.label = self._translation.get("order")
        order_container.expand = True
        self._add_to_inputs(
            {
                "order_date": FieldGroup(
                    label=self._get_label("order_date", 0, colon=False),
                    input=(order_date_container, 4),
                    marker=self._get_marker("order_date", 0),
                ),
                "customer_id": FieldGroup(
                    label=self._get_label("customer", 0, colon=False),
                    input=(customer_container, 4),
                    marker=self._get_marker("customer_id", 0),
                ),
                "order_id": FieldGroup(
                    label=self._get_label("order", 0, colon=False),
                    input=(order_container, 4),
                    marker=self._get_marker("order_id", 0),
                ),
            }
        )

        self.__item_bulk_transfer = BulkTransfer(
            on_save_clicked=on_save_clicked,
            source_label=self._translation.get("order_items"),
            target_label=self._translation.get("order_items"),
            on_move_requested=on_move_requested,
            on_pending_reverted=on_pending_reverted,
            allow_duplicate_targets=True,
            source_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("quantity"),
            ],
            target_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("source_bin"),
                self._translation.get("quantity"),
            ],
        )
        self.__item_bulk_transfer.set_enabled_states(False, False, False)

        self.__package_bulk_transfer = BulkTransfer(
            on_save_clicked=on_package_save_clicked,
            source_label=self._translation.get("packages"),
            target_label=self._translation.get("packages"),
            on_move_requested=on_package_move_requested,
            on_pending_reverted=on_package_pending_reverted,
            allow_duplicate_targets=True,
            source_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("quantity"),
            ],
            target_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("source_bin"),
                self._translation.get("quantity"),
            ],
        )
        self.__package_bulk_transfer.set_enabled_states(False, False, False)
        self.__complete_button = ft.Button(
            content=self._translation.get("confirm"),
            on_click=lambda _: self._controller.on_complete_status_clicked(),
            disabled=True,
        )
        complete_row = ft.Row(
            controls=[self.__complete_button],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        inputs_row = ft.ResponsiveRow(
            columns=12,
            spacing=8,
            run_spacing=8,
            controls=[
                order_date_container,
                customer_container,
                order_container,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self._master_column.controls = [
            inputs_row,
            self.__item_bulk_transfer,
            self.__package_bulk_transfer,
            complete_row,
        ]
        self.content = ft.Container(content=self._master_column, expand=True)

    def set_orders(self, orders: list[tuple[int, str]]) -> None:
        self.__order_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(order_id), text=label) for order_id, label in orders
        ]
        if self.__order_input.page:
            self.__order_input.update()

    def set_customers(self, customers: list[tuple[int, str]]) -> None:
        self.__customer_input.options = [ft.dropdown.Option(key="0", text="")] + [
            ft.dropdown.Option(key=str(customer_id), text=label) for customer_id, label in customers
        ]
        if self.__customer_input.page:
            self.__customer_input.update()

    def reset_order_selection(self) -> None:
        self.__order_input.value = "0"
        if self.__order_input.page:
            self.__order_input.update()

    def set_order_error(self, message: str | None) -> None:
        self.__order_input.error_text = message
        if self.__order_input.page:
            self.__order_input.update()

    def set_source_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__item_bulk_transfer.set_source_rows(rows)

    def set_target_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__item_bulk_transfer.set_target_rows(rows)

    def mark_source_items_as_moved(self, ids: list[int]) -> None:
        self.__item_bulk_transfer.mark_source_items_as_moved(ids)

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return self.__item_bulk_transfer.get_pending_targets()

    def add_target_row(self, source_id: int, values: list[str]) -> int:
        return self.__item_bulk_transfer.add_target_row(source_id, cast(list[Any], values), highlight=True)

    def update_existing_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        self.__item_bulk_transfer.update_existing_target(target_id, source_id, cast(list[Any], values))

    def set_source_enabled(self, enabled: bool) -> None:
        self.__item_bulk_transfer.set_source_enabled(enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__item_bulk_transfer.set_target_enabled(enabled)

    def set_package_source_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__package_bulk_transfer.set_source_rows(rows)

    def set_package_target_rows(self, rows: list[tuple[int, list[Any]]]) -> None:
        self.__package_bulk_transfer.set_target_rows(rows)

    def set_package_source_enabled(self, enabled: bool) -> None:
        self.__package_bulk_transfer.set_source_enabled(enabled)

    def set_package_target_enabled(self, enabled: bool) -> None:
        self.__package_bulk_transfer.set_target_enabled(enabled)

    def set_package_enabled_states(self, source_enabled: bool, target_enabled: bool, buttons_enabled: bool) -> None:
        self.__package_bulk_transfer.set_enabled_states(source_enabled, target_enabled, buttons_enabled)

    def set_complete_button_enabled(self, enabled: bool) -> None:
        self.__complete_button.disabled = not enabled
        if self.__complete_button.page:
            self.__complete_button.update()

    def get_pending_package_targets(self) -> list[tuple[int, int]]:
        return self.__package_bulk_transfer.get_pending_targets()

    def add_package_target_row(self, source_id: int, values: list[str]) -> int:
        return self.__package_bulk_transfer.add_target_row(source_id, cast(list[Any], values), highlight=True)

    def update_existing_package_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        self.__package_bulk_transfer.update_existing_target(target_id, source_id, cast(list[Any], values))
    def __handle_order_changed(self) -> None:
        self._controller.on_order_changed(self.__order_input.value)

    def __handle_order_date_changed(self) -> None:
        self._controller.on_order_date_changed(self.__order_date_input.value)

    def __handle_customer_changed(self) -> None:
        self._controller.on_customer_changed(self.__customer_input.value)

