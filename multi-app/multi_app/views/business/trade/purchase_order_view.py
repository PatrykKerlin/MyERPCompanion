from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from views.controls.bulk_transfer_control import BulkTransfer
from views.controls.data_table_control import DataTable
from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.business.trade.purchase_order_controller import PurchaseOrderController


class PurchaseOrderView(BaseView):
    def __init__(
        self,
        controller: PurchaseOrderController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        suppliers: list[tuple[int, str]],
        currencies: list[tuple[int, str]],
        statuses: list[tuple[int, str]],
        source_items: list[tuple[int, list[str]]],
        target_items: list[tuple[int, list[str]]],
        status_history: list[dict[str, Any]],
        bulk_transfer_enabled: bool,
        supplier_currency_by_id: dict[int, int],
        on_items_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_items_move_requested: Callable[[list[int]], None] | None = None,
        on_items_delete_clicked: Callable[[list[int]], None] | None = None,
        on_items_pending_reverted: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__create_defaults: dict[str, Any] = {}
        self.__editable_keys = {"supplier_id", "notes", "internal_notes"}
        self.__pending_source_items = list(source_items)
        self.__pending_target_items = list(target_items)
        self.__pending_totals: dict[str, float] = {}
        self.__is_mounted = False
        self.__bulk_transfer_enabled_in_read = bulk_transfer_enabled
        self.__supplier_currency_by_id = supplier_currency_by_id

        main_fields_definitions = [
            {
                "key": "supplier_id",
                "input": self._get_dropdown,
                "options": suppliers,
                "callbacks": [self.__handle_supplier_changed],
            },
            {"key": "status_id", "input": self._get_dropdown, "options": statuses},
            {"key": "currency_id", "input": self._get_dropdown, "options": currencies},
            {"key": "number", "input": self._get_text_input},
            {"key": "order_date", "input": self._get_date_picker},
            {"key": "tracking_number", "input": self._get_text_input},
            {"key": "shipping_cost", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_net", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_vat", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_gross", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_discount", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
        ]
        notes_fields_definitions = [
            {"key": "notes", "input": self._get_text_input, "lines": 4},
            {"key": "internal_notes", "input": self._get_text_input, "lines": 4},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        notes_fields = self._build_field_groups(notes_fields_definitions)
        self._add_to_inputs(main_fields, notes_fields)
        main_grid = self._build_grid(main_fields)
        notes_grid = self._build_grid(notes_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(
                controls=main_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid + notes_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self.__bulk_transfer = BulkTransfer(
            on_save_clicked=on_items_save_clicked or (lambda _: None),
            source_label=self._translation.get("items"),
            target_label=self._translation.get("order_items"),
            on_move_requested=on_items_move_requested,
            on_delete_clicked=on_items_delete_clicked,
            on_pending_reverted=on_items_pending_reverted,
            allow_duplicate_targets=True,
            source_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("ean"),
            ],
            target_columns=[
                self._translation.get("index"),
                self._translation.get("name"),
                self._translation.get("quantity"),
            ],
        )
        self.__bulk_transfer.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        bulk_transfer_row = ft.Row(controls=[self.__bulk_transfer])
        self.__status_history_table = DataTable(
            columns=["status", "created_at"],
            rows=status_history,
            translation=self._translation,
            height=180,
            with_button=False,
            on_row_clicked=None,
            read_only=True,
            visible=mode in {ViewMode.READ, ViewMode.EDIT},
        )
        self._master_column.controls.extend(
            [
                self._columns_row,
                ft.Row(height=25),
                bulk_transfer_row,
                ft.Row(height=15),
                self.__status_history_table,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )

    def did_mount(self):
        result = super().did_mount()
        self.__is_mounted = True
        if self._mode == ViewMode.CREATE:
            self.__apply_supplier_currency()
        self.__bulk_transfer.set_source_rows(cast(list[tuple[int, list[Any]]], self.__pending_source_items))
        self.__bulk_transfer.set_target_rows(cast(list[tuple[int, list[Any]]], self.__pending_target_items))
        if self.__pending_totals:
            self.__apply_order_totals(self.__pending_totals)
            self.__pending_totals.clear()
        return result

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode == ViewMode.CREATE:
            self.__create_defaults = self._controller.get_create_defaults()
            self.__apply_create_defaults()
            self.__apply_supplier_currency()
        if mode != ViewMode.READ:
            self.__apply_editable_fields(mode)
        self.__bulk_transfer.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()
        self.__status_history_table.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__status_history_table.read_only = True
        if self.__status_history_table.page:
            self.__status_history_table.update()

    def __apply_create_defaults(self) -> None:
        for key, value in self.__create_defaults.items():
            if key in self._inputs:
                input_control = self._inputs[key].input.content
                if hasattr(input_control, "value"):
                    setattr(input_control, "value", value)
                    if input_control:
                        input_control.update()
            if key in self._inputs:
                self._controller.set_field_value(key, value)
        if "is_sales" in self.__create_defaults:
            self._controller.set_hidden_field_value("is_sales", self.__create_defaults["is_sales"])
        if "delivery_method_id" in self.__create_defaults:
            self._controller.set_hidden_field_value("delivery_method_id", self.__create_defaults["delivery_method_id"])

    def __apply_editable_fields(self, mode: ViewMode) -> None:
        for key, field in self._inputs.items():
            input_control = field.input.content
            if mode == ViewMode.EDIT:
                editable = key == "status_id"
            else:
                editable = mode == ViewMode.CREATE and key in self.__editable_keys
            if hasattr(input_control, "read_only"):
                setattr(input_control, "read_only", not editable)
            if hasattr(input_control, "disabled") and not editable:
                setattr(input_control, "disabled", True)
            if input_control:
                input_control.update()

    def __set_bulk_transfer_state(self, mode: ViewMode) -> None:
        enabled = mode == ViewMode.READ and self.__bulk_transfer_enabled_in_read
        self.__bulk_transfer.set_enabled_states(enabled, enabled, enabled)

    def __handle_supplier_changed(self) -> None:
        self.__apply_supplier_currency()

    def __apply_supplier_currency(self) -> None:
        supplier_id = self.__get_selected_supplier_id()
        if supplier_id is None:
            return
        currency_id = self.__supplier_currency_by_id.get(supplier_id)
        self.__set_currency_value(currency_id)

    def __get_selected_supplier_id(self) -> int | None:
        field = self._inputs.get("supplier_id")
        if not field:
            return None
        input_control = field.input.content
        if not isinstance(input_control, ft.Dropdown):
            return None
        value = input_control.value
        if value is None:
            return None
        value = value.strip()
        if value in {"", "0"}:
            return None
        return int(value) if value.isdigit() else None

    def __set_currency_value(self, currency_id: int | None) -> None:
        field = self._inputs.get("currency_id")
        if not field:
            return
        input_control = field.input.content
        if not isinstance(input_control, ft.Dropdown):
            return
        if currency_id is None:
            input_control.value = "0"
            self._controller.set_field_value("currency_id", None)
        else:
            input_control.value = str(currency_id)
            self._controller.set_field_value("currency_id", currency_id)
        if input_control:
            input_control.update()

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return self.__bulk_transfer.get_pending_targets()

    def set_source_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_source_rows(cast(list[tuple[int, list[Any]]], rows))

    def set_target_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_target_rows(cast(list[tuple[int, list[Any]]], rows))

    def add_target_row(self, source_id: int, values: list[str], highlight: bool = True) -> int:
        return self.__bulk_transfer.add_target_row(source_id, cast(list[Any], values), highlight=highlight)

    def update_existing_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        self.__bulk_transfer.update_existing_target(target_id, source_id, cast(list[Any], values))

    def set_order_totals(self, total_net: float, total_vat: float, total_gross: float, total_discount: float) -> None:
        totals = {
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_discount": total_discount,
        }
        if not self.__is_mounted:
            self.__pending_totals = totals
            for key, value in totals.items():
                self._controller.set_field_value(key, value)
            return
        self.__apply_order_totals(totals)

    def __apply_order_totals(self, totals: dict[str, float]) -> None:
        for key, value in totals.items():
            if key in self._inputs:
                input_control = self._inputs[key].input.content
                if hasattr(input_control, "value"):
                    setattr(input_control, "value", value)
                    if input_control:
                        input_control.update()
                self._controller.set_field_value(key, value)
