from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from views.controls.bulk_transfer_control import BulkTransfer
from views.controls.data_table_control import DataTable
from utils.translation import Translation
from schemas.business.trade.order_view_schema import OrderViewDiscountSchema

if TYPE_CHECKING:
    from controllers.business.trade.sales_order_controller import SalesOrderController


class SalesOrderView(BaseView):
    def __init__(
        self,
        controller: SalesOrderController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        customers: list[tuple[int, str]],
        currencies: list[tuple[int, str]],
        statuses: list[tuple[int, str]],
        delivery_methods: list[tuple[int, str]],
        categories: list[tuple[int, str]],
        source_items: list[tuple[int, list[str]]],
        source_item_categories: dict[int, int | None],
        customer_discounts: dict[int, list[OrderViewDiscountSchema]],
        category_discounts: dict[int, list[OrderViewDiscountSchema]],
        item_discounts: dict[int, list[OrderViewDiscountSchema]],
        selected_item_discounts: dict[int, int | None],
        target_items: list[tuple[int, list[str]]],
        status_history: list[dict[str, Any]],
        bulk_transfer_enabled: bool,
        on_items_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_items_move_requested: Callable[[list[int]], None] | None = None,
        on_items_delete_clicked: Callable[[list[int]], None] | None = None,
        on_items_pending_reverted: Callable[[list[int]], None] | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        self.__create_defaults: dict[str, Any] = {}
        self.__editable_keys = {"customer_id", "delivery_method_id", "currency_id", "notes", "internal_notes"}
        self.__all_source_items = list(source_items)
        self.__source_item_category_map = dict(source_item_categories)
        self.__customer_discount_map = dict(customer_discounts)
        self.__category_discount_map = dict(category_discounts)
        self.__item_discount_map = dict(item_discounts)
        self.__selected_customer_discount_id: int | None = None
        self.__selected_category_discount_id: int | None = None
        self.__selected_item_discount_ids: dict[int, int | None] = dict(selected_item_discounts)
        self.__selected_category_id: int | None = None
        self.__pending_source_items: list[tuple[int, list[str]]] = []
        self.__pending_target_items = list(target_items)
        self.__pending_totals: dict[str, float] = {}
        self.__is_mounted = False
        self.__bulk_transfer_enabled_in_read = bulk_transfer_enabled

        main_fields_definitions = [
            {
                "key": "customer_id",
                "input": self._get_dropdown,
                "options": customers,
                "callbacks": [self.__on_customer_changed],
            },
            {"key": "delivery_method_id", "input": self._get_dropdown, "options": delivery_methods},
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

        self.__customer_discount = ft.Dropdown(
            options=self.__get_customer_discount_options(self.__get_selected_customer_id()),
            value="0",
            on_select=self.__on_customer_discount_changed,
            expand=True,
        )
        self.__customer_discount_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                self._get_label("discount", 4, colon=True)[0],
                ft.Container(
                    content=self.__customer_discount,
                    col={"sm": 8.0},
                    alignment=self._base_alignment,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.__customer_discount_row.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__customer_discount.disabled = mode == ViewMode.EDIT

        main_grid.append(self.__customer_discount_row)

        category_options = [ft.dropdown.Option("all", self._translation.get("all"))]
        category_options.extend(ft.dropdown.Option(str(category_id), label) for category_id, label in categories)
        self.__category_filter = ft.Dropdown(
            options=category_options,
            value="all",
            on_select=self.__on_category_filter_changed,
            expand=True,
        )
        self.__category_filter.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__category_filter.disabled = mode == ViewMode.EDIT
        self.__category_discount = ft.Dropdown(
            options=self.__get_category_discount_options(None),
            value="0",
            on_select=self.__on_category_discount_changed,
            expand=True,
        )
        self.__category_discount.visible = self.__category_filter.visible
        self.__category_discount.disabled = self.__category_filter.disabled
        self.__category_filter_row = ft.Row(
            controls=[
                ft.Text(self._translation.get("category")),
                self.__category_filter,
                ft.Text(self._translation.get("discount")),
                self.__category_discount,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.__category_filter_row.visible = self.__category_filter.visible

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
                self._translation.get("stock_quantity"),
                self._translation.get("reserved_quantity"),
                self._translation.get("discount"),
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
                ft.Row(height=10),
                self.__category_filter_row,
                ft.Row(height=15),
                bulk_transfer_row,
                ft.Row(height=15),
                self.__status_history_table,
                ft.Row(height=25),
                self._buttons_row,
            ]
        )
        self.__pending_source_items = self.__get_filtered_source_items()

    def did_mount(self):
        result = super().did_mount()
        self.__is_mounted = True
        self.__bulk_transfer.set_source_rows(self.__pending_source_items)
        self.__bulk_transfer.set_target_rows(self.__pending_target_items)
        self.__apply_customer_discount_options()
        self.__apply_category_discount_options()
        if self.__pending_totals:
            self.__apply_order_totals(self.__pending_totals)
            self.__pending_totals.clear()
        return result

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if mode == ViewMode.CREATE:
            self.__create_defaults = self._controller.get_create_defaults()
            self.__apply_create_defaults()
        if mode != ViewMode.READ:
            self.__apply_editable_fields(mode)
        self.__bulk_transfer.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__bulk_transfer.height = 260 if self.__bulk_transfer.visible else 0
        self.__set_bulk_transfer_state(mode)
        self.__bulk_transfer.clear_pending_changes()
        self.__status_history_table.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__status_history_table.read_only = True
        self.__category_filter.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__category_filter.disabled = mode == ViewMode.EDIT
        self.__category_filter_row.visible = self.__category_filter.visible
        self.__category_discount.visible = self.__category_filter.visible
        self.__category_discount.disabled = self.__category_filter.disabled
        self.__customer_discount_row.visible = mode in {ViewMode.READ, ViewMode.EDIT}
        self.__customer_discount.disabled = mode == ViewMode.EDIT
        if self.__bulk_transfer.visible:
            self.__apply_category_filter()
        if self.__category_filter.page:
            self.__category_filter.update()
        if self.__category_filter_row.page:
            self.__category_filter_row.update()
        if self.__category_discount.page:
            self.__category_discount.update()
        if self.__customer_discount_row.page:
            self.__customer_discount_row.update()
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

    def get_pending_targets(self) -> list[tuple[int, int]]:
        return self.__bulk_transfer.get_pending_targets()

    def set_source_rows(self, rows: list[tuple[int, list[object]]]) -> None:
        self.__all_source_items = list(rows)
        self.__apply_category_filter()

    def set_source_data(
        self,
        rows: list[tuple[int, list[str]]],
        category_map: dict[int, int | None],
        item_discounts: dict[int, list[OrderViewDiscountSchema]] | None = None,
        selected_item_discounts: dict[int, int | None] | None = None,
    ) -> None:
        self.__all_source_items = list(rows)
        self.__source_item_category_map = dict(category_map)
        if item_discounts is not None:
            self.__item_discount_map = dict(item_discounts)
        if selected_item_discounts is not None:
            self.__selected_item_discount_ids = dict(selected_item_discounts)
        self.__apply_category_filter()

    def set_target_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self.__bulk_transfer.set_target_rows(rows)

    def add_target_row(self, source_id: int, values: list[str], highlight: bool = True) -> int:
        return self.__bulk_transfer.add_target_row(source_id, values, highlight=highlight)

    def update_existing_target(self, target_id: int, source_id: int, values: list[str]) -> None:
        self.__bulk_transfer.update_existing_target(target_id, source_id, values)

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

    def set_shipping_cost(self, shipping_cost: float) -> None:
        if "shipping_cost" in self._inputs:
            input_control = self._inputs["shipping_cost"].input.content
            if hasattr(input_control, "value"):
                setattr(input_control, "value", shipping_cost)
                if input_control:
                    input_control.update()
        self._controller.set_field_value("shipping_cost", shipping_cost)

    def __apply_order_totals(self, totals: dict[str, float]) -> None:
        for key, value in totals.items():
            if key in self._inputs:
                input_control = self._inputs[key].input.content
                if hasattr(input_control, "value"):
                    setattr(input_control, "value", value)
                    if input_control:
                        input_control.update()
                self._controller.set_field_value(key, value)

    def __on_category_filter_changed(self, event: ft.Event[ft.Dropdown]) -> None:
        value = event.control.value
        if not value or value == "all":
            self.__selected_category_id = None
        else:
            try:
                self.__selected_category_id = int(value)
            except ValueError:
                self.__selected_category_id = None
        self._controller.set_selected_category_id(self.__selected_category_id)
        self.__apply_category_discount_options()
        self.__apply_category_filter()

    def __on_category_discount_changed(self, event: ft.Event[ft.Dropdown]) -> None:
        self.__selected_category_discount_id = self.__parse_dropdown_value(event.control.value)
        self._controller.set_category_discount_id(self.__selected_category_id, self.__selected_category_discount_id)

    def __on_customer_changed(self) -> None:
        self.__apply_customer_discount_options()
        self.__selected_customer_discount_id = None
        self._controller.set_customer_discount_id(None)

    def __on_customer_discount_changed(self, event: ft.Event[ft.Dropdown]) -> None:
        self.__selected_customer_discount_id = self.__parse_dropdown_value(event.control.value)
        self._controller.set_customer_discount_id(self.__selected_customer_discount_id)

    def __apply_category_filter(self) -> None:
        rows = self.__get_filtered_source_items()
        if not self.__is_mounted:
            self.__pending_source_items = rows
            return
        self.__bulk_transfer.set_source_rows(rows)

    def __get_filtered_source_items(self) -> list[tuple[int, list[str]]]:
        if self.__selected_category_id is None:
            return self.__build_source_rows_with_discounts(self.__all_source_items)
        filtered = [
            (item_id, values)
            for item_id, values in self.__all_source_items
            if self.__source_item_category_map.get(item_id) == self.__selected_category_id
        ]
        return self.__build_source_rows_with_discounts(filtered)

    def __build_source_rows_with_discounts(
        self, rows: list[tuple[int, list[str]]]
    ) -> list[tuple[int, list[object]]]:
        results: list[tuple[int, list[object]]] = []
        for item_id, values in rows:
            discount_dropdown = self.__build_item_discount_dropdown(item_id)
            results.append((item_id, list(values) + [discount_dropdown]))
        return results

    def __build_item_discount_dropdown(self, item_id: int) -> ft.Dropdown:
        options = self.__get_item_discount_options(item_id)
        selected = self.__selected_item_discount_ids.get(item_id)
        dropdown = ft.Dropdown(
            options=options,
            value="0" if selected is None else str(selected),
            on_select=lambda event, item_id=item_id: self.__on_item_discount_changed(event, item_id),
            expand=True,
            disabled=self._mode == ViewMode.EDIT or not self.__bulk_transfer_enabled_in_read,
        )
        return dropdown

    def __on_item_discount_changed(self, event: ft.Event[ft.Dropdown], item_id: int) -> None:
        discount_id = self.__parse_dropdown_value(event.control.value)
        self.__selected_item_discount_ids[item_id] = discount_id
        self._controller.set_item_discount_id(item_id, discount_id)

    def __apply_customer_discount_options(self) -> None:
        customer_id = self.__get_selected_customer_id()
        self.__customer_discount.options = self.__get_customer_discount_options(customer_id)
        self.__customer_discount.value = "0"
        if self.__customer_discount.page:
            self.__customer_discount.update()

    def __apply_category_discount_options(self) -> None:
        self.__category_discount.options = self.__get_category_discount_options(self.__selected_category_id)
        self.__category_discount.value = "0"
        self.__selected_category_discount_id = None
        self._controller.set_category_discount_id(self.__selected_category_id, None)
        if self.__category_discount.page:
            self.__category_discount.update()

    def __get_customer_discount_options(self, customer_id: int | None) -> list[ft.dropdown.Option]:
        discounts = self.__customer_discount_map.get(customer_id or -1, [])
        options = [ft.dropdown.Option("0", "")]
        options.extend(ft.dropdown.Option(str(discount.id), discount.code) for discount in discounts)
        return options

    def __get_category_discount_options(self, category_id: int | None) -> list[ft.dropdown.Option]:
        discounts = self.__category_discount_map.get(category_id or -1, [])
        options = [ft.dropdown.Option("0", "")]
        options.extend(ft.dropdown.Option(str(discount.id), discount.code) for discount in discounts)
        return options

    def __get_item_discount_options(self, item_id: int) -> list[ft.dropdown.Option]:
        discounts = self.__item_discount_map.get(item_id, [])
        options = [ft.dropdown.Option("0", "")]
        options.extend(ft.dropdown.Option(str(discount.id), discount.code) for discount in discounts)
        return options

    def __get_selected_customer_id(self) -> int | None:
        if "customer_id" not in self._inputs:
            return None
        input_control = self._inputs["customer_id"].input.content
        if hasattr(input_control, "value"):
            return self.__parse_dropdown_value(getattr(input_control, "value", None))
        return None

    @staticmethod
    def __parse_dropdown_value(value: str | None) -> int | None:
        if not value or value == "0":
            return None
        try:
            return int(value)
        except ValueError:
            return None
