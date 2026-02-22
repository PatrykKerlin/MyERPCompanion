from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ControlStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.controls.bulk_transfer_control import BulkTransfer
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.trade.purchase_order_controller import PurchaseOrderController


class PurchaseOrderView(BaseView):
    def __init__(
        self,  # NOSONAR
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
        show_details = self._is_details_mode(mode)
        self.__create_defaults: dict[str, Any] = {}
        self.__editable_keys = {"supplier_id", "notes"}
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
                "callbacks": [self.__on_supplier_changed],
            },
            {"key": "currency_id", "input": self._get_dropdown, "options": currencies},
            {"key": "status_id", "input": self._get_dropdown, "options": statuses},
            {"key": "number", "input": self._get_text_input},
            {"key": "order_date", "input": self._get_date_picker},
            {"key": "tracking_number", "input": self._get_text_input},
            {"key": "shipping_cost", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_net", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_vat", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_gross", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "total_discount", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
        ]
        notes_field_definition = [{"key": "notes", "input": self._get_text_input, "lines": 3}]
        main_fields = self._build_field_groups(main_fields_definitions)
        notes_field = self._build_field_groups(notes_field_definition)
        self._add_to_inputs(main_fields, notes_field)
        main_grid = self._build_grid(main_fields)
        notes_grid = self._build_grid(notes_field)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)
        self.__buttons_spacing_row = ft.Row(
            height=AppDimensions.SPACE_2XL,
            visible=show_details,
        )
        self.__status_history_table = DataTable(
            columns=["status", "created_at"],
            rows=status_history,
            translation=self._translation,
            height=AppDimensions.SECTION_HEIGHT_COMPACT,
            with_button=False,
            on_row_clicked=None,
            read_only=True,
            visible=show_details,
            with_border=True,
        )
        self.__status_history_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                self._get_label("status_history", 4, colon=True)[0],
                ft.Container(
                    content=self.__status_history_table,
                    col={"sm": 8.0},
                    alignment=ControlStyles.INPUT_ALIGNMENT,
                ),
            ],
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
            visible=show_details,
        )

        columns = [
            ft.Column(controls=main_grid + self._spacing_responsive_row + [self.__status_history_row], expand=True),
            self._spacing_column,
            ft.Column(
                controls=meta_grid
                + self._spacing_responsive_row
                + notes_grid
                + (2 * self._spacing_responsive_row)
                + [self._spacing_row, self._buttons_row],
                expand=True,
            ),
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
            cancel_label=self._translation.get("cancel"),
            confirm_label=self._translation.get("ok"),
            delete_confirm_title=self._translation.get("confirm"),
            delete_confirm_message=self._translation.get("delete_selected_items_q"),
        )
        self.__bulk_transfer.visible = show_details
        self.__bulk_transfer.height = AppDimensions.BULK_TRANSFER_HEIGHT_LARGE if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        bulk_transfer_row = ft.Row(controls=[self.__bulk_transfer])
        self._master_column.controls.extend([self._columns_row, self.__buttons_spacing_row, bulk_transfer_row])

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode == ViewMode.CREATE:
            self.__create_defaults = self._controller.get_create_defaults()
            self.__apply_create_defaults()
            self.__apply_supplier_currency()
        if mode in {ViewMode.CREATE, ViewMode.EDIT}:
            self.__apply_editable_fields(mode)
        show_details = self._is_details_mode(mode)
        self.__bulk_transfer.visible = show_details
        self.__bulk_transfer.height = AppDimensions.BULK_TRANSFER_HEIGHT_LARGE if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()
        self.__status_history_table.visible = show_details
        self.__status_history_table.read_only = True
        self.__status_history_row.visible = show_details
        self.__buttons_spacing_row.visible = show_details
        if self.__buttons_spacing_row.page:
            self.__buttons_spacing_row.update()
        if self.__status_history_row.page:
            self.__status_history_row.update()
        if self.__status_history_table.page:
            self.__status_history_table.update()

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
                editable = key in {"status_id", "notes"}
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

    def __on_supplier_changed(self) -> None:
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

    def __apply_order_totals(self, totals: dict[str, float]) -> None:
        for key, value in totals.items():
            if key in self._inputs:
                input_control = self._inputs[key].input.content
                if hasattr(input_control, "value"):
                    setattr(input_control, "value", value)
                    if input_control:
                        input_control.update()
                self._controller.set_field_value(key, value)
