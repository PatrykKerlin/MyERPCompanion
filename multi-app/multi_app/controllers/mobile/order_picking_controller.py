from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.logistic.unit_schema import UnitPlainSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService, UnitService
from services.business.trade import AssocOrderItemService, AssocOrderStatusService, CustomerService, OrderService, StatusService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.mobile.order_picking_view import OrderPickingView


@dataclass(frozen=True)
class OrderPickingItemRow:
    item_id: int
    item_index: str
    item_name: str
    to_process: int


@dataclass(frozen=True)
class OrderPickedItemRow:
    item_id: int
    item_index: str
    item_name: str
    bin_location: str
    quantity: int


@dataclass(frozen=True)
class OrderPickingBinOption:
    bin_item_id: int
    bin_id: int
    location: str
    available_quantity: int
    bin_item_quantity: int


class OrderPickingController(
    BaseViewController[OrderService, OrderPickingView, OrderPlainSchema, OrderStrictSchema]
):
    _plain_schema_cls = OrderPlainSchema
    _strict_schema_cls = OrderStrictSchema
    _service_cls = OrderService
    _view_cls = OrderPickingView
    _endpoint = Endpoint.ORDERS
    _view_key = View.ORDER_PICKING

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__unit_service = UnitService(self._settings, self._logger, self._tokens_accessor)
        self.__bin_item_service = AssocBinItemService(self._settings, self._logger, self._tokens_accessor)
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__units_by_id: dict[int, UnitPlainSchema] = {}

        self.__orders: list[OrderPlainSchema] = []
        self.__selected_order_date: str | None = date.today().isoformat()
        self.__selected_customer_id: int | None = None
        self.__selected_order_id: int | None = None
        self.__order_items_request_id = 0

        self.__current_rows: list[OrderPickingItemRow] = []
        self.__items_by_id: dict[int, ItemPlainSchema] = {}
        self.__package_items_by_id: dict[int, ItemPlainSchema] = {}

        self.__active_pick_item_id: int | None = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options: dict[int, OrderPickingBinOption] = {}

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> OrderPickingView:
        customers = await self.__perform_get_customers() or []
        customer_pairs = [(customer.id, self.__format_customer_label(customer)) for customer in customers]
        self.__orders = await self.__load_eligible_orders(self.__selected_order_date, self.__selected_customer_id)
        self.__selected_order_id = self.__resolve_selected_order_id(event.data)

        view = OrderPickingView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
            customers=customer_pairs,
            default_order_date=self.__selected_order_date_for_view(),
            selected_customer_id=self.__selected_customer_id,
        )
        view.set_orders(
            orders=[(schema.id, schema.number) for schema in self.__orders],
            selected_order_id=self.__selected_order_id,
        )
        package_options = await self.__load_package_picker_options(self.__selected_order_id)
        view.set_package_options(
            options=package_options,
            enabled=self.__selected_order_id is not None and bool(package_options),
        )
        if self.__selected_order_id is not None:
            to_pick_rows, picked_rows = await self.__load_order_item_rows(self.__selected_order_id)
            view.set_order_items(to_pick_rows)
            view.set_picked_items(picked_rows)
        return view

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_order_selected(self, order_id: int | None) -> None:
        self.__selected_order_id = order_id
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self.__order_items_request_id += 1
        request_id = self.__order_items_request_id
        self._page.run_task(self.__load_items_for_selected_order, order_id, request_id)

    def on_order_date_changed(self, value: str | None) -> None:
        normalized_value = self.__normalize_order_date_string(value)
        self.__selected_order_date = normalized_value
        self._page.run_task(self.__reload_orders)

    def on_customer_changed(self, value: str | None) -> None:
        if not value or value == "0":
            self.__selected_customer_id = None
        else:
            try:
                self.__selected_customer_id = int(value)
            except ValueError:
                self.__selected_customer_id = None
        self._page.run_task(self.__reload_orders)

    def on_order_item_selected(self, item_id: int) -> None:
        self._page.run_task(self.__open_item_pick_form, item_id)

    def on_package_item_selected(self, item_id: int | None) -> None:
        if self.__selected_order_id is None:
            return
        if item_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        self._page.run_task(self.__open_item_pick_form, item_id, True)

    def on_pick_form_cancelled(self) -> None:
        if not isinstance(self._view, OrderPickingView):
            return
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self._view.show_items_list()
        self._page.update()

    def on_pick_form_saved(self, bin_id: int | None, quantity: int | None) -> None:
        if self.__active_pick_is_package:
            self._page.run_task(self.__save_package_pick, bin_id, quantity)
            return
        self._page.run_task(self.__save_item_pick, bin_id, quantity)

    async def __load_items_for_selected_order(self, order_id: int | None, request_id: int) -> None:
        to_pick_rows: list[OrderPickingItemRow] = []
        picked_rows: list[OrderPickedItemRow] = []
        package_options: list[tuple[int, str]] = []
        if order_id is not None:
            to_pick_rows, picked_rows = await self.__load_order_item_rows(order_id)
            package_options = await self.__load_package_picker_options(order_id)
        if request_id != self.__order_items_request_id:
            return
        if not isinstance(self._view, OrderPickingView):
            return
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self._view.show_items_list()
        self._view.set_package_options(
            options=package_options,
            enabled=order_id is not None and bool(package_options),
        )
        self._view.set_order_items(to_pick_rows)
        self._view.set_picked_items(picked_rows)
        self._page.update()

    async def __reload_orders(self) -> None:
        if not isinstance(self._view, OrderPickingView):
            return
        self.__orders = await self.__load_eligible_orders(self.__selected_order_date, self.__selected_customer_id)
        self.__selected_order_id = None
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self.__current_rows = []
        self.__items_by_id = {}
        self.__package_items_by_id = {}
        self.__order_items_request_id += 1
        self._view.set_orders(orders=[(schema.id, schema.number) for schema in self.__orders], selected_order_id=None)
        self._view.reset_order_selection()
        self._view.set_package_options([], enabled=False)
        self._view.show_items_list()
        self._view.set_order_items([])
        self._view.set_picked_items([])
        self._page.update()

    async def __load_eligible_orders(
        self, order_date: str | None, customer_id: int | None
    ) -> list[OrderPlainSchema]:
        return await self.__perform_get_eligible_orders(order_date, customer_id)

    async def __load_order_item_rows(self, order_id: int) -> tuple[list[OrderPickingItemRow], list[OrderPickedItemRow]]:
        order_items = await self.__perform_get_order_items(order_id) or []
        if not order_items:
            self.__current_rows = []
            self.__items_by_id = {}
            return [], []

        remaining_items = [schema for schema in order_items if schema.to_process > 0]

        item_ids = sorted({schema.item_id for schema in order_items})
        items = await self.__perform_get_items_by_ids(item_ids) or []
        self.__items_by_id = {schema.id: schema for schema in items}

        to_pick_rows: list[OrderPickingItemRow] = []
        quantity_by_item: dict[int, int] = {}
        for order_item in remaining_items:
            quantity_by_item[order_item.item_id] = quantity_by_item.get(order_item.item_id, 0) + max(0, order_item.to_process)
        for item_id, to_process in quantity_by_item.items():
            item_schema = self.__items_by_id.get(item_id)
            if not item_schema or item_schema.is_package:
                continue
            to_pick_rows.append(
                OrderPickingItemRow(
                    item_id=item_schema.id,
                    item_index=item_schema.index,
                    item_name=item_schema.name,
                    to_process=to_process,
                )
            )
        to_pick_rows = sorted(to_pick_rows, key=lambda row: (row.item_index.lower(), row.item_name.lower()))

        picked_quantity_by_item_bin: dict[tuple[int, int], int] = {}
        for order_item in order_items:
            if order_item.bin_id is None:
                continue
            item_schema = self.__items_by_id.get(order_item.item_id)
            if not item_schema:
                continue
            picked_quantity = max(order_item.quantity - order_item.to_process, 0)
            if picked_quantity <= 0:
                continue
            key = (order_item.item_id, order_item.bin_id)
            picked_quantity_by_item_bin[key] = picked_quantity_by_item_bin.get(key, 0) + picked_quantity

        bin_ids = sorted({bin_id for _, bin_id in picked_quantity_by_item_bin.keys()})
        bins = await self.__perform_get_bins_by_ids(bin_ids) if bin_ids else []
        locations_by_bin_id = {schema.id: schema.location for schema in bins}

        picked_rows: list[OrderPickedItemRow] = []
        for (item_id, bin_id), quantity in picked_quantity_by_item_bin.items():
            item_schema = self.__items_by_id.get(item_id)
            if item_schema is None:
                continue
            picked_rows.append(
                OrderPickedItemRow(
                    item_id=item_id,
                    item_index=item_schema.index,
                    item_name=item_schema.name,
                    bin_location=locations_by_bin_id.get(bin_id, str(bin_id)),
                    quantity=quantity,
                )
            )
        picked_rows = sorted(
            picked_rows,
            key=lambda row: (row.item_index.lower(), row.item_name.lower(), row.bin_location.lower()),
        )

        self.__current_rows = to_pick_rows
        return to_pick_rows, picked_rows

    async def __open_item_pick_form(self, item_id: int, is_package_pick: bool = False) -> None:
        if not isinstance(self._view, OrderPickingView) or self.__selected_order_id is None:
            return
        max_pick_quantity = 0
        item_schema: ItemPlainSchema | None = None
        if is_package_pick:
            item_schema = self.__package_items_by_id.get(item_id)
            if item_schema is None:
                items = await self.__perform_get_items_by_ids([item_id]) or []
                if not items:
                    return
                item_schema = items[0]
                self.__package_items_by_id[item_id] = item_schema
            max_pick_quantity = self.__resolve_package_pick_limit(item_schema)
        else:
            selected_row = next((row for row in self.__current_rows if row.item_id == item_id), None)
            if not selected_row or selected_row.to_process <= 0:
                return
            item_schema = self.__items_by_id.get(item_id)
            if item_schema is None:
                items = await self.__perform_get_items_by_ids([item_id]) or []
                if not items:
                    return
                item_schema = items[0]
                self.__items_by_id[item_id] = item_schema
            max_pick_quantity = selected_row.to_process

        bin_options = await self.__load_pick_bin_options(item_id=item_id, max_quantity=max_pick_quantity)
        if not bin_options:
            self._open_error_dialog(message_key="no_bins")
            return

        default_bin_id = bin_options[0].bin_id
        default_quantity = (
            1 if is_package_pick and bin_options[0].available_quantity > 0 else min(max_pick_quantity, bin_options[0].available_quantity)
        )
        if default_quantity <= 0:
            self._open_error_dialog(message_key="insufficient_stock")
            return

        self.__active_pick_item_id = item_id
        self.__active_pick_is_package = is_package_pick
        self.__active_pick_bin_options = {option.bin_id: option for option in bin_options}
        unit_name = await self.__resolve_unit_name(item_schema.unit_id)
        self._view.show_pick_form(
            item=item_schema,
            to_process=max_pick_quantity,
            bin_options=[
                (option.bin_id, option.location, option.bin_item_quantity, option.available_quantity)
                for option in bin_options
            ],
            default_bin_id=default_bin_id,
            default_quantity=default_quantity,
            unit_name=unit_name,
            is_package_pick=is_package_pick,
        )
        self._page.update()

    @staticmethod
    def __resolve_package_pick_limit(item_schema: ItemPlainSchema) -> int:
        return max(1, item_schema.outbound_quantity, item_schema.stock_quantity)

    async def __resolve_unit_name(self, unit_id: int) -> str | None:
        unit_schema = self.__units_by_id.get(unit_id)
        if unit_schema is not None:
            return unit_schema.name
        unit_schemas = await self.__perform_get_units() or []
        self.__units_by_id = {schema.id: schema for schema in unit_schemas}
        unit_schema = self.__units_by_id.get(unit_id)
        if unit_schema is None:
            return None
        return unit_schema.name

    async def __load_pick_bin_options(self, item_id: int, max_quantity: int) -> list[OrderPickingBinOption]:
        bin_item_schemas = await self.__perform_get_bin_items_for_item(item_id) or []
        if not bin_item_schemas:
            return []

        bin_ids = sorted({schema.bin_id for schema in bin_item_schemas})
        bins = await self.__perform_get_bins_by_ids(bin_ids) or []
        bins_by_id = {schema.id: schema for schema in bins}
        warehouse_id = self.__resolve_mobile_warehouse_id()

        options: list[OrderPickingBinOption] = []
        for bin_item in bin_item_schemas:
            if bin_item.quantity <= 0:
                continue
            bin_schema = bins_by_id.get(bin_item.bin_id)
            if not bin_schema or not bin_schema.is_outbound:
                continue
            if warehouse_id is not None and bin_schema.warehouse_id != warehouse_id:
                continue
            available_quantity = min(bin_item.quantity, max_quantity)
            if available_quantity <= 0:
                continue
            options.append(
                OrderPickingBinOption(
                    bin_item_id=bin_item.id,
                    bin_id=bin_item.bin_id,
                    location=bin_schema.location,
                    available_quantity=available_quantity,
                    bin_item_quantity=bin_item.quantity,
                )
            )
        return sorted(options, key=lambda option: option.location.lower())

    async def __save_item_pick(self, bin_id: int | None, quantity: int | None) -> None:
        if not isinstance(self._view, OrderPickingView):
            return
        if self.__selected_order_id is None or self.__active_pick_item_id is None:
            return
        if bin_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        if quantity is None or quantity <= 0:
            self._open_error_dialog(message_key="value_required")
            return

        selected_option = self.__active_pick_bin_options.get(bin_id)
        if selected_option is None:
            self._open_error_dialog(message_key="value_required")
            return

        order_items = await self.__perform_get_order_items(self.__selected_order_id) or []
        if not order_items:
            self._open_error_dialog(message_key=ApiActionError.FETCH)
            return
        item_ids = sorted({schema.item_id for schema in order_items})
        item_schemas = await self.__perform_get_items_by_ids(item_ids) or []
        item_map = {schema.id: schema for schema in item_schemas}

        active_item_id = self.__active_pick_item_id
        order_rows_for_item = []
        for row in order_items:
            if row.item_id != active_item_id or row.to_process <= 0:
                continue
            item_schema_for_row = item_map.get(row.item_id)
            if not item_schema_for_row or item_schema_for_row.is_package:
                continue
            order_rows_for_item.append(row)
        if not order_rows_for_item:
            self._open_error_dialog(message_key="insufficient_stock")
            return

        max_to_process = sum(row.to_process for row in order_rows_for_item)
        effective_quantity = min(quantity, selected_option.available_quantity, max_to_process)
        if effective_quantity <= 0:
            self._open_error_dialog(message_key="insufficient_stock")
            return

        await self.__apply_pick_updates(
            order_items=order_items,
            item_map=item_map,
            item_id=active_item_id,
            bin_option=selected_option,
            moved_quantity=effective_quantity,
        )

        await self.__check_and_update_order_status(self.__selected_order_id, {active_item_id})
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self._view.show_items_list()
        to_pick_rows, picked_rows = await self.__load_order_item_rows(self.__selected_order_id)
        self._view.set_order_items(to_pick_rows)
        self._view.set_picked_items(picked_rows)
        self._page.update()

    async def __save_package_pick(self, bin_id: int | None, quantity: int | None) -> None:
        if not isinstance(self._view, OrderPickingView):
            return
        if self.__selected_order_id is None or self.__active_pick_item_id is None:
            return
        if bin_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        if quantity is None or quantity <= 0:
            self._open_error_dialog(message_key="value_required")
            return
        selected_option = self.__active_pick_bin_options.get(bin_id)
        if selected_option is None:
            self._open_error_dialog(message_key="value_required")
            return
        effective_quantity = min(quantity, selected_option.available_quantity)
        if effective_quantity <= 0:
            self._open_error_dialog(message_key="insufficient_stock")
            return

        new_bin_quantity = max(0, selected_option.bin_item_quantity - effective_quantity)
        if new_bin_quantity > 0:
            await self.__perform_update_bin_items(
                [
                    AssocBinItemStrictSchema(
                        id=selected_option.bin_item_id,
                        bin_id=selected_option.bin_id,
                        item_id=self.__active_pick_item_id,
                        quantity=new_bin_quantity,
                    )
                ]
            )
        else:
            await self.__perform_delete_bin_items([selected_option.bin_item_id])

        await self.__perform_create_order_items(
            [
                AssocOrderItemStrictSchema(
                    order_id=self.__selected_order_id,
                    item_id=self.__active_pick_item_id,
                    quantity=effective_quantity,
                    total_net=0,
                    total_vat=0,
                    total_gross=0,
                    total_discount=0,
                    to_process=0,
                    bin_id=selected_option.bin_id,
                    category_discount_id=None,
                    customer_discount_id=None,
                    item_discount_id=None,
                )
            ]
        )

        package_item_schema = self.__package_items_by_id.get(self.__active_pick_item_id)
        if package_item_schema is None:
            package_items = await self.__perform_get_items_by_ids([self.__active_pick_item_id]) or []
            if package_items:
                package_item_schema = package_items[0]
                self.__package_items_by_id[self.__active_pick_item_id] = package_item_schema
        if package_item_schema is not None:
            new_stock = max(0, package_item_schema.stock_quantity - effective_quantity)
            await self.__perform_update_item(
                self.__active_pick_item_id,
                self.__build_item_update(package_item_schema, new_stock),
            )

        await self.__check_and_update_order_status(self.__selected_order_id, set())
        self.__active_pick_item_id = None
        self.__active_pick_is_package = False
        self.__active_pick_bin_options = {}
        self._view.show_items_list()
        to_pick_rows, picked_rows = await self.__load_order_item_rows(self.__selected_order_id)
        self._view.set_order_items(to_pick_rows)
        self._view.set_picked_items(picked_rows)
        package_options = await self.__load_package_picker_options(self.__selected_order_id)
        self._view.set_package_options(options=package_options, enabled=bool(package_options))
        self._page.update()

    async def __apply_pick_updates(
        self,
        order_items: list[AssocOrderItemPlainSchema],
        item_map: dict[int, ItemPlainSchema],
        item_id: int,
        bin_option: OrderPickingBinOption,
        moved_quantity: int,
    ) -> None:
        new_bin_quantity = max(0, bin_option.bin_item_quantity - moved_quantity)
        if new_bin_quantity > 0:
            await self.__perform_update_bin_items(
                [
                    AssocBinItemStrictSchema(
                        id=bin_option.bin_item_id,
                        bin_id=bin_option.bin_id,
                        item_id=item_id,
                        quantity=new_bin_quantity,
                    )
                ]
            )
        else:
            await self.__perform_delete_bin_items([bin_option.bin_item_id])

        order_item_states: dict[int, dict[str, Any]] = {}
        for order_item in order_items:
            order_item_states[order_item.id] = {
                "order_id": order_item.order_id,
                "item_id": order_item.item_id,
                "quantity": order_item.quantity,
                "total_net": order_item.total_net,
                "total_vat": order_item.total_vat,
                "total_gross": order_item.total_gross,
                "total_discount": order_item.total_discount,
                "to_process": order_item.to_process,
                "bin_id": order_item.bin_id,
                "category_discount_id": order_item.category_discount_id,
                "customer_discount_id": order_item.customer_discount_id,
                "item_discount_id": order_item.item_discount_id,
            }

        order_rows_by_item: dict[int, list[AssocOrderItemPlainSchema]] = {}
        for order_item in order_items:
            item_schema = item_map.get(order_item.item_id)
            if not item_schema or item_schema.is_package or order_item.to_process <= 0:
                continue
            order_rows_by_item.setdefault(order_item.item_id, []).append(order_item)

        remaining = moved_quantity
        ordered_rows = [row for row in order_rows_by_item.get(item_id, []) if row.bin_id == bin_option.bin_id and row.to_process > 0] + [
            row for row in order_rows_by_item.get(item_id, []) if row.bin_id is None and row.to_process > 0
        ]
        order_item_creates: list[AssocOrderItemStrictSchema] = []
        for order_item in ordered_rows:
            if remaining <= 0:
                break
            state = order_item_states.get(order_item.id)
            if not state:
                continue
            to_process = int(state["to_process"])
            if to_process <= 0:
                continue
            take = min(to_process, remaining)
            if take <= 0:
                continue
            bin_assigned = state["bin_id"] is not None
            quantity = int(state["quantity"])
            if not bin_assigned and take < to_process and quantity > 0:
                picked_ratio = take / quantity
                picked_total_net = round(float(state["total_net"]) * picked_ratio, 2)
                picked_total_vat = round(float(state["total_vat"]) * picked_ratio, 2)
                picked_total_gross = round(float(state["total_gross"]) * picked_ratio, 2)
                picked_total_discount = round(float(state["total_discount"]) * picked_ratio, 2)
                state["quantity"] = max(0, quantity - take)
                state["total_net"] = round(float(state["total_net"]) - picked_total_net, 2)
                state["total_vat"] = round(float(state["total_vat"]) - picked_total_vat, 2)
                state["total_gross"] = round(float(state["total_gross"]) - picked_total_gross, 2)
                state["total_discount"] = round(float(state["total_discount"]) - picked_total_discount, 2)
                state["to_process"] = max(0, to_process - take)
                order_item_creates.append(
                    AssocOrderItemStrictSchema(
                        order_id=int(state["order_id"]),
                        item_id=int(state["item_id"]),
                        quantity=take,
                        total_net=picked_total_net,
                        total_vat=picked_total_vat,
                        total_gross=picked_total_gross,
                        total_discount=picked_total_discount,
                        to_process=0,
                        bin_id=bin_option.bin_id,
                        category_discount_id=state["category_discount_id"],
                        customer_discount_id=state["customer_discount_id"],
                        item_discount_id=state["item_discount_id"],
                    )
                )
            else:
                state["to_process"] = max(0, to_process - take)
                if state["to_process"] == 0 and not bin_assigned:
                    state["bin_id"] = bin_option.bin_id
            remaining -= take

        order_item_updates: list[AssocOrderItemStrictSchema] = []
        for order_item in order_items:
            state = order_item_states.get(order_item.id)
            if not state:
                continue
            if (
                state["quantity"] != order_item.quantity
                or state["total_net"] != order_item.total_net
                or state["total_vat"] != order_item.total_vat
                or state["total_gross"] != order_item.total_gross
                or state["total_discount"] != order_item.total_discount
                or state["to_process"] != order_item.to_process
                or state["bin_id"] != order_item.bin_id
            ):
                order_item_updates.append(
                    AssocOrderItemStrictSchema(
                        id=order_item.id,
                        order_id=int(state["order_id"]),
                        item_id=int(state["item_id"]),
                        quantity=int(state["quantity"]),
                        total_net=float(state["total_net"]),
                        total_vat=float(state["total_vat"]),
                        total_gross=float(state["total_gross"]),
                        total_discount=float(state["total_discount"]),
                        to_process=int(state["to_process"]),
                        bin_id=state["bin_id"],
                        category_discount_id=state["category_discount_id"],
                        customer_discount_id=state["customer_discount_id"],
                        item_discount_id=state["item_discount_id"],
                    )
                )

        if order_item_updates:
            await self.__perform_update_order_items(order_item_updates)
        if order_item_creates:
            await self.__perform_create_order_items(order_item_creates)

        item_schema = item_map.get(item_id)
        if item_schema:
            new_stock = max(0, item_schema.stock_quantity - moved_quantity)
            await self.__perform_update_item(item_id, self.__build_item_update(item_schema, new_stock))

    def __resolve_mobile_warehouse_id(self) -> int | None:
        user = self._state_store.app_state.user.current
        if user and user.warehouse_id is not None:
            return user.warehouse_id
        return None

    async def __check_and_update_order_status(self, order_id: int, touched_item_ids: set[int]) -> None:
        statuses = await self.__perform_get_all_statuses()
        status_by_order = {status.order: status for status in statuses}
        order_statuses = await self.__perform_get_order_statuses(order_id)
        if not order_statuses:
            return
        latest_status = max(order_statuses, key=lambda status: status.created_at)
        current_status = status_by_order.get(latest_status.status_id)
        if current_status is None:
            current_status = next((status for status in statuses if status.id == latest_status.status_id), None)
        current_order_value = current_status.order if current_status else None
        if current_order_value == 2 and touched_item_ids:
            next_status = status_by_order.get(3) or next((status for status in statuses if status.order == 3), None)
            if next_status:
                has_status = any(status.status_id == next_status.id for status in order_statuses)
                if not has_status:
                    await self.__perform_create_order_status(
                        AssocOrderStatusStrictSchema(order_id=order_id, status_id=next_status.id)
                    )
                current_order_value = 3

        final_status = status_by_order.get(4) or next((status for status in statuses if status.order == 4), None)
        if not final_status or current_order_value == 4:
            return

        order_items = await self.__perform_get_order_items(order_id) or []
        if not order_items:
            return

        has_pending_items = any(order_item.to_process > 0 for order_item in order_items)
        if has_pending_items:
            return

        item_ids = sorted({order_item.item_id for order_item in order_items})
        item_schemas = await self.__perform_get_items_by_ids(item_ids) or []
        items_by_id = {item.id: item for item in item_schemas}
        has_picked_packages = any(
            (
                (item_schema := items_by_id.get(order_item.item_id)) is not None
                and item_schema.is_package
                and order_item.bin_id is not None
                and max(order_item.quantity - order_item.to_process, 0) > 0
            )
            for order_item in order_items
        )
        if not has_picked_packages:
            if touched_item_ids:
                self._open_message_dialog(message_key="package_required_to_complete")
            return

        has_final_status = any(status.status_id == final_status.id for status in order_statuses)
        if has_final_status:
            return

        if current_order_value in {2, 3}:
            await self.__perform_create_order_status(
                AssocOrderStatusStrictSchema(order_id=order_id, status_id=final_status.id)
            )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_eligible_orders(
        self, order_date: str | None, customer_id: int | None
    ) -> list[OrderPlainSchema]:
        query_params: dict[str, str | int] = {
            "sort_by": "number",
            "order": "asc",
        }
        if order_date is not None:
            query_params["order_date"] = order_date
        if customer_id is not None:
            query_params["customer_id"] = customer_id
        return await self._service.get_all(
            Endpoint.ORDERS_PICKING_ELIGIBLE,
            None,
            query_params,
            None,
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customers(self) -> list[CustomerPlainSchema]:
        return await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_items(self, order_id: int) -> list[AssocOrderItemPlainSchema]:
        return await self.__order_item_service.get_all(
            Endpoint.ORDER_ITEMS, None, {"order_id": order_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_items(self) -> list[ItemPlainSchema]:
        return await self.__item_service.get_all(Endpoint.ITEMS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_by_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        if not item_ids:
            return []
        body_params = IdsPayloadSchema(ids=item_ids)
        items = await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)
        normalized_items: list[ItemPlainSchema] = []
        for item in items:
            item_data = item.model_dump()
            self._parse_data_row(item_data)
            normalized_items.append(ItemPlainSchema.model_validate(item_data))
        return normalized_items

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_bin_items_for_item(self, item_id: int) -> list[AssocBinItemPlainSchema]:
        return await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, {"item_id": item_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_bins_by_ids(self, bin_ids: list[int]) -> list[BinPlainSchema]:
        if not bin_ids:
            return []
        body_params = IdsPayloadSchema(ids=bin_ids)
        return await self.__bin_service.get_bulk(Endpoint.BINS_GET_BULK, None, None, body_params, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_units(self) -> list[UnitPlainSchema]:
        return await self.__unit_service.get_all(Endpoint.UNITS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_statuses(self, order_id: int) -> list[AssocOrderStatusPlainSchema]:
        return await self.__order_status_service.get_all(
            Endpoint.ORDER_STATUSES, None, {"order_id": order_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_status(self, payload: AssocOrderStatusStrictSchema) -> None:
        await self.__order_status_service.create(Endpoint.ORDER_STATUSES, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.update_bulk(Endpoint.BIN_ITEMS_UPDATE_BULK, None, None, items, self._module_id)

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_bin_items(self, ids: list[int]) -> None:
        body_params = IdsPayloadSchema(ids=ids)
        await self.__bin_item_service.delete_bulk(
            Endpoint.BIN_ITEMS_DELETE_BULK, None, None, body_params, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.update_bulk(
            Endpoint.ORDER_ITEMS_UPDATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.create_bulk(
            Endpoint.ORDER_ITEMS_CREATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_item(self, item_id: int, payload: ItemStrictSchema) -> None:
        await self.__item_service.update(Endpoint.ITEMS, item_id, None, payload, self._module_id)

    @staticmethod
    def __resolve_selected_order_id(data: dict[str, Any] | None) -> int | None:
        if not data:
            return None
        selected_order_id = data.get("selected_order_id")
        if isinstance(selected_order_id, int):
            return selected_order_id
        return None

    @staticmethod
    def __format_customer_label(customer: CustomerPlainSchema) -> str:
        if customer.company_name:
            return customer.company_name
        name_parts = [part for part in [customer.first_name, customer.last_name] if part]
        return " ".join(name_parts) if name_parts else str(customer.id)

    async def __load_package_picker_options(self, order_id: int | None) -> list[tuple[int, str]]:
        if order_id is None:
            self.__package_items_by_id = {}
            return []
        all_items = await self.__perform_get_all_items() or []
        package_items = [
            item
            for item in all_items
            if item.is_package and item.outbound_quantity > 0
        ]
        package_items = sorted(package_items, key=lambda item: (item.index.lower(), item.name.lower()))
        self.__package_items_by_id = {item.id: item for item in package_items}
        return [(item.id, f"{item.index} | {item.name}") for item in package_items]

    def __selected_order_date_for_view(self) -> date | None:
        if self.__selected_order_date is None:
            return None
        return self.__parse_iso_date(self.__selected_order_date)

    @staticmethod
    def __normalize_order_date_string(value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        value_stripped = value.strip()
        if value_stripped == "":
            return None
        parsed = OrderPickingController.__parse_iso_date(value_stripped)
        if parsed is None:
            return None
        return parsed.isoformat()

    @staticmethod
    def __parse_iso_date(value: str) -> date | None:
        candidate = value[:10]
        try:
            return date.fromisoformat(candidate)
        except ValueError:
            return None

    @staticmethod
    def __build_item_update(item: ItemPlainSchema, stock_quantity: int) -> ItemStrictSchema:
        return ItemStrictSchema(
            index=item.index,
            name=item.name,
            ean=item.ean,
            description=item.description,
            purchase_price=item.purchase_price,
            vat_rate=item.vat_rate,
            margin=item.margin,
            is_available=item.is_available,
            is_fragile=item.is_fragile,
            is_package=item.is_package,
            is_returnable=item.is_returnable,
            width=item.width,
            height=item.height,
            length=item.length,
            weight=item.weight,
            expiration_date=item.expiration_date,
            stock_quantity=stock_quantity,
            min_stock_level=item.min_stock_level,
            max_stock_level=item.max_stock_level,
            moq=item.moq,
            category_id=item.category_id,
            unit_id=item.unit_id,
            supplier_id=item.supplier_id,
            lead_time=item.lead_time,
        )
