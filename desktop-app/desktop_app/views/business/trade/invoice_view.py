from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from controllers.business.trade.invoice_controller import InvoiceController


class InvoiceView(BaseView):
    def __init__(
        self,
        controller: InvoiceController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
        customers: list[tuple[int, str]],
        on_orders_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
        on_orders_delete_clicked: Callable[[list[int]], None],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__create_defaults: dict[str, Any] = {}
        self.__locked_keys = {"number", "issue_date", "due_date"}
        self.__editable_keys = {
            "is_paid",
            "currency_id",
            "customer_id",
        }
        self.__pending_totals: dict[str, float] = {}
        self.__is_mounted = False
        main_fields_definitions = [
            {"key": "number", "input": self._get_text_input},
            {"key": "issue_date", "input": self._get_date_picker},
            {"key": "due_date", "input": self._get_date_picker},
            {"key": "is_paid", "input": self._get_checkbox},
            {"key": "total_net", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_vat", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_gross", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_discount", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "currency_id", "input": self._get_dropdown, "options": currencies},
            {"key": "customer_id", "input": self._get_dropdown, "options": customers},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(
                controls=main_grid,
                expand=3,
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)

        self.__bulk_transfer = BulkTransfer(
            on_save_clicked=on_orders_save_clicked,
            source_label=self._translation.get("orders"),
            target_label=self._translation.get("orders"),
            on_delete_clicked=on_orders_delete_clicked,
            allow_duplicate_targets=False,
            source_columns=[
                self._translation.get("number"),
                self._translation.get("order_date"),
                self._translation.get("total_gross"),
            ],
            target_columns=[
                self._translation.get("number"),
                self._translation.get("order_date"),
                self._translation.get("total_gross"),
            ],
        )
        self.__bulk_transfer.visible = mode in {ViewMode.CREATE, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        bulk_transfer_row = ft.Row(controls=[self.__bulk_transfer])

        self._master_column.controls.extend(self._rows)
        self._master_column.controls.insert(-1, ft.Row(height=15))
        self._master_column.controls.insert(-1, bulk_transfer_row)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode == ViewMode.CREATE:
            self.__create_defaults = self._controller.get_create_defaults()
            self.__apply_create_defaults()
        if mode != ViewMode.READ:
            self.__apply_editable_fields(mode)
        self.__bulk_transfer.visible = mode in {ViewMode.CREATE, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__bulk_transfer.clear_pending_changes()
        if self.__bulk_transfer.page:
            self.__bulk_transfer.update()

    def did_mount(self):
        result = super().did_mount()
        self.__is_mounted = True
        if self.__pending_totals:
            self.__apply_pending_totals()
        return result

    def set_number(self, number: str) -> None:
        self.__set_field_value("number", number)

    def set_issue_date(self, value: Any) -> None:
        self.__set_field_value("issue_date", value)

    def set_due_date(self, value: Any) -> None:
        self.__set_field_value("due_date", value)

    def set_total_net(self, value: float) -> None:
        self.__set_total_value("total_net", value)

    def set_total_vat(self, value: float) -> None:
        self.__set_total_value("total_vat", value)

    def set_total_gross(self, value: float) -> None:
        self.__set_total_value("total_gross", value)

    def set_total_discount(self, value: float) -> None:
        self.__set_total_value("total_discount", value)

    def set_order_totals(self, totals: dict[str, float]) -> None:
        self.__pending_totals = dict(totals)
        if self.__is_mounted:
            self.__apply_pending_totals()

    def set_source_rows(self, rows: list[tuple[int, list[object]]]) -> None:
        self.__bulk_transfer.set_source_rows(rows)

    def set_target_rows(self, rows: list[tuple[int, list[object]]]) -> None:
        self.__bulk_transfer.set_target_rows(rows)

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return self.__bulk_transfer.get_pending_targets()

    def mark_source_orders_as_moved(self, ids: list[int]) -> None:
        self.__bulk_transfer.mark_source_items_as_moved(ids)

    def set_source_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_source_enabled(enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_target_enabled(enabled)

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

    def __apply_editable_fields(self, mode: ViewMode) -> None:
        for key, field in self._inputs.items():
            input_control = field.input.content
            if mode == ViewMode.EDIT:
                editable = key in {"is_paid"}
            else:
                editable = mode == ViewMode.CREATE and key in self.__editable_keys
            if key in self.__locked_keys:
                editable = False
            if key in {"total_net", "total_vat", "total_gross", "total_discount"}:
                editable = False
            if hasattr(input_control, "read_only"):
                setattr(input_control, "read_only", not editable)
            if hasattr(input_control, "disabled") and not editable:
                setattr(input_control, "disabled", True)
            if hasattr(input_control, "disabled") and editable:
                setattr(input_control, "disabled", False)
            if input_control:
                input_control.update()

    def __set_total_value(self, key: str, value: float) -> None:
        if not self.__is_mounted:
            self.__pending_totals[key] = value
            return
        self.__set_field_value(key, value)

    def __apply_pending_totals(self) -> None:
        totals = dict(self.__pending_totals)
        self.__pending_totals.clear()
        for key, value in totals.items():
            self.__set_field_value(key, value)

    def __set_field_value(self, key: str, value: Any) -> None:
        field = self._inputs.get(key)
        if not field:
            return
        input_control = field.input.content
        if hasattr(input_control, "value"):
            setattr(input_control, "value", value)
            if input_control:
                input_control.update()
        self._controller.set_field_value(key, value)
