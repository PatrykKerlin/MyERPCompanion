from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from views.controls.bulk_transfer_control import BulkTransfer
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
        create_defaults: dict[str, Any] | None,
        suppliers: list[tuple[int, str]],
        currencies: list[tuple[int, str]],
        delivery_methods: list[tuple[int, str]],
        source_items: list[tuple[int, str]],
        target_items: list[tuple[int, str]],
        on_items_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_items_move_requested: Callable[[list[int]], None] | None = None,
        on_items_delete_clicked: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__create_defaults = create_defaults or {}
        self.__editable_keys = {"supplier_id", "delivery_method_id", "currency_id", "notes", "internal_notes"}
        self.__pending_source_items = list(source_items)
        self.__pending_target_items = list(target_items)

        main_fields_definitions = [
            {"key": "supplier_id", "input": self._get_dropdown, "options": suppliers},
            {"key": "delivery_method_id", "input": self._get_dropdown, "options": delivery_methods},
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
        )
        self.__bulk_transfer.visible = mode == ViewMode.READ
        self.__set_bulk_transfer_state(mode)
        bulk_transfer_row = ft.Row(
            controls=[ft.Container(content=self.__bulk_transfer, expand=True, height=260)],
        )
        self._master_column.controls.extend(
            [
                self._columns_row,
                ft.Row(height=25),
                bulk_transfer_row,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )

    def did_mount(self):
        self.__bulk_transfer.set_source_items(self.__pending_source_items)
        self.__bulk_transfer.set_target_items(self.__pending_target_items)
        return super().did_mount()

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode == ViewMode.CREATE:
            self.__create_defaults = self._controller.get_create_defaults()
            self.__apply_create_defaults()
        self.__apply_editable_fields(mode)
        self.__bulk_transfer.visible = mode == ViewMode.READ
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()

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

    def __apply_editable_fields(self, mode: ViewMode) -> None:
        allow_edit = mode in {ViewMode.CREATE, ViewMode.EDIT}
        for key, field in self._inputs.items():
            input_control = field.input.content
            editable = allow_edit and key in self.__editable_keys
            if hasattr(input_control, "read_only"):
                setattr(input_control, "read_only", not editable)
            if hasattr(input_control, "disabled") and not editable:
                setattr(input_control, "disabled", True)
            if input_control:
                input_control.update()

    def __set_bulk_transfer_state(self, mode: ViewMode) -> None:
        enabled = mode == ViewMode.READ
        self.__bulk_transfer.set_enabled_states(enabled, enabled, enabled)

    def get_pending_item_ids(self) -> list[int]:
        return self.__bulk_transfer.get_pending_move_ids()

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_source_items(items)

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_target_items(items)

    def move_source_items(self, item_ids: list[int], highlight: bool) -> None:
        self.__bulk_transfer.move_source_items(item_ids, highlight=highlight)
