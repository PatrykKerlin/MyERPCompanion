import asyncio
from datetime import date
from typing import Any
import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from services.business.trade import (
    AssocOrderItemService,
    AssocOrderStatusService,
    CustomerService,
    OrderService,
    StatusService,
)
from schemas.business.trade.customer_schema import CustomerPlainSchema
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.order_picking_view import OrderPickingView
from views.components.bin_quantity_dialog_component import BinQuantityDialogComponent


class OrderPickingController(
    BaseViewController[AssocBinItemService, OrderPickingView, AssocBinItemPlainSchema, AssocBinItemStrictSchema]
):
    _plain_schema_cls = AssocBinItemPlainSchema
    _strict_schema_cls = AssocBinItemStrictSchema
    _service_cls = AssocBinItemService
    _view_cls = OrderPickingView
    _endpoint = Endpoint.BIN_ITEMS
    _view_key = View.ORDER_PICKING

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__bin_item_service = self._service
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)

        self.__order_items: dict[int, AssocOrderItemPlainSchema] = {}
        self.__order_items_by_item: dict[int, list[AssocOrderItemPlainSchema]] = {}
        self.__order_item_quantities: dict[int, int] = {}
        self.__order_item_original_quantities: dict[int, int] = {}
        self.__order_item_labels: dict[int, tuple[str, str]] = {}
        self.__items_by_id: dict[int, ItemPlainSchema] = {}
        self.__package_items_by_id: dict[int, ItemPlainSchema] = {}
        self.__package_item_quantities: dict[int, int] = {}
        self.__pending_moves: dict[int, tuple[int, int, int, int, int, str, int]] = {}
        self.__package_pending_moves: dict[int, tuple[int, int, int, int, int, str, int]] = {}
        self.__saved_target_rows: list[tuple[int, list[Any]]] = []
        self.__target_rows: list[tuple[int, list[Any]]] = []
        self.__package_saved_target_rows: list[tuple[int, list[Any]]] = []
        self.__package_target_rows: list[tuple[int, list[Any]]] = []
        self.__current_order_id: int | None = None
        self.__selected_order_date: date | None = date.today()
        self.__selected_customer_id: int | None = None

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> OrderPickingView:
        mode = ViewMode.STATIC
        customers = await self.__perform_get_customers()
        customer_pairs = [(customer.id, self.__format_customer_label(customer)) for customer in customers]
        orders = await self.__load_eligible_orders(self.__selected_order_date, self.__selected_customer_id)
        order_pairs = [(order.id, order.number) for order in orders]
        view = OrderPickingView(
            self,
            translation,
            mode,
            event.view_key,
            customer_pairs,
            self.__selected_order_date,
            order_pairs,
            self.on_bulk_transfer_save_clicked,
            self.on_bulk_transfer_move_requested,
            self.on_bulk_transfer_pending_reverted,
            self.on_package_save_clicked,
            self.on_package_move_requested,
            self.on_package_pending_reverted,
        )
        await self.__load_package_items(view)
        return view

    def on_order_changed(self, value: str | None) -> None:
        if not self._view:
            return
        if not value or value == "0":
            self._view.set_order_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_order_error(None)
        order_id = int(value)
        self.__current_order_id = order_id
        self._page.run_task(self.__load_order_items, order_id)

    def on_order_date_changed(self, value: date | None) -> None:
        self.__selected_order_date = value
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

    def on_bulk_transfer_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_bulk_transfer_save)

    def on_bulk_transfer_move_requested(self, selected_ids: list[int]) -> None:
        if not self._view or not selected_ids:
            return
        item_id = selected_ids[0]
        max_quantity = self.__order_item_quantities.get(item_id, 0)
        pending_quantity = sum(
            qty for pending_item, _, _, _, qty, _, _ in self.__pending_moves.values() if pending_item == item_id
        )
        max_quantity = max(0, max_quantity - pending_quantity)
        if max_quantity <= 0:
            return
        self._page.run_task(self.__handle_move_with_quantity, item_id, max_quantity)

    def on_bulk_transfer_pending_reverted(self, target_ids: list[int]) -> None:
        for target_id in target_ids:
            self.__pending_moves.pop(target_id, None)
        self.__refresh_source_rows()
        self.__refresh_target_rows()

    def on_package_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_package_save)

    def on_package_move_requested(self, selected_ids: list[int]) -> None:
        if not self._view or not selected_ids:
            return
        item_id = selected_ids[0]
        max_quantity = self.__package_item_quantities.get(item_id, 0)
        pending_quantity = sum(
            qty for pending_item, _, _, _, qty, _, _ in self.__package_pending_moves.values() if pending_item == item_id
        )
        max_quantity = max(0, max_quantity - pending_quantity)
        if max_quantity <= 0:
            return
        self._page.run_task(self.__handle_package_move_with_quantity, item_id, max_quantity)

    def on_package_pending_reverted(self, target_ids: list[int]) -> None:
        for target_id in target_ids:
            self.__package_pending_moves.pop(target_id, None)
        self.__refresh_package_source_rows()
        self.__refresh_package_target_rows()

    def on_complete_status_clicked(self) -> None:
        if not self._view or self.__current_order_id is None:
            return
        if not self.__can_complete_order():
            return
        self._page.run_task(self.__handle_complete_status)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_eligible_orders(
        self, order_date: date | None, customer_id: int | None
    ) -> list[OrderPlainSchema]:
        query_params: dict[str, str | int] = {
            "sort_by": "number",
            "order": "asc",
        }
        if order_date is not None:
            query_params["order_date"] = order_date.isoformat()
        if customer_id is not None:
            query_params["customer_id"] = customer_id
        return await self.__order_service.get_all(
            Endpoint.ORDERS_PICKING_ELIGIBLE,
            None,
            query_params,
            None,
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_statuses(self, order_id: int) -> list[AssocOrderStatusPlainSchema]:
        return await self.__order_status_service.get_all(
            Endpoint.ORDER_STATUSES, None, {"order_id": order_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customers(self) -> list[CustomerPlainSchema]:
        return await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_items(self) -> list[ItemPlainSchema]:
        return await self.__item_service.get_all(Endpoint.ITEMS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_items(self, order_id: int) -> list[AssocOrderItemPlainSchema]:
        return await self.__order_item_service.get_all(
            Endpoint.ORDER_ITEMS, None, {"order_id": order_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_by_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        if not item_ids:
            return []
        body_params = IdsPayloadSchema(ids=item_ids)
        return await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)

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

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_status(self, payload: AssocOrderStatusStrictSchema) -> None:
        await self.__order_status_service.create(Endpoint.ORDER_STATUSES, None, None, payload, self._module_id)

    async def __load_eligible_orders(self, order_date: date | None, customer_id: int | None) -> list[OrderPlainSchema]:
        return await self.__perform_get_eligible_orders(order_date, customer_id)

    async def __load_package_items(self, view: OrderPickingView | None = None) -> None:
        items = await self.__perform_get_all_items()
        self.__package_items_by_id = {item.id: item for item in items if item.is_package}
        self.__package_item_quantities = {
            item_id: max(item.outbound_quantity, 0)
            for item_id, item in self.__package_items_by_id.items()
            if item.outbound_quantity > 0
        }
        if view:
            view.set_package_source_rows(self.__build_package_source_rows())
            view.set_package_source_enabled(bool(self.__package_item_quantities))
            self.__update_package_transfer_state()

    def __build_package_source_rows(self) -> list[tuple[int, list[Any]]]:
        rows: list[tuple[int, list[Any]]] = []
        for item_id, available in self.__package_item_quantities.items():
            if available <= 0:
                continue
            item = self.__package_items_by_id.get(item_id)
            if not item:
                continue
            rows.append((item_id, [item.index, item.name, str(available)]))
        return rows

    def __can_complete_order(self) -> bool:
        if self.__current_order_id is None:
            return False
        remaining_source = any(
            max(
                0,
                quantity
                - sum(
                    qty for pending_item, _, _, _, qty, _, _ in self.__pending_moves.values() if pending_item == item_id
                ),
            )
            > 0
            for item_id, quantity in self.__order_item_quantities.items()
        )
        has_packages = bool(self.__package_saved_target_rows)
        return (not remaining_source) and has_packages

    def __update_complete_button_state(self) -> None:
        if not self._view:
            return
        self._view.set_complete_button_enabled(self.__can_complete_order())

    def __update_package_transfer_state(self) -> None:
        if not self._view:
            return
        enabled = bool(self.__current_order_id) and bool(self.__package_item_quantities)
        self._view.set_package_enabled_states(enabled, enabled, enabled)

    async def __reload_orders(self) -> None:
        if not self._view:
            return
        orders = await self.__load_eligible_orders(self.__selected_order_date, self.__selected_customer_id)
        order_pairs = [(order.id, order.number) for order in orders]
        self._view.set_orders(order_pairs)
        self._view.reset_order_selection()
        self.__current_order_id = None
        self.__pending_moves.clear()
        self.__package_pending_moves.clear()
        self.__order_items = {}
        self.__order_items_by_item = {}
        self.__order_item_quantities = {}
        self.__order_item_original_quantities = {}
        self.__order_item_labels = {}
        self.__items_by_id = {}
        self.__saved_target_rows = []
        self.__target_rows = []
        self.__package_saved_target_rows = []
        self.__package_target_rows = []
        self._view.set_source_rows([])
        self._view.set_target_rows([])
        self._view.set_source_enabled(False)
        self._view.set_target_enabled(False)
        self._view.set_package_target_rows([])
        self._view.set_package_source_rows(self.__build_package_source_rows())
        self._view.set_package_source_enabled(bool(self.__package_item_quantities))
        self._view.set_package_target_enabled(False)
        self.__update_package_transfer_state()
        self._view.set_complete_button_enabled(False)

    @staticmethod
    def __format_customer_label(customer: CustomerPlainSchema) -> str:
        if customer.company_name:
            return customer.company_name
        name_parts = [part for part in [customer.first_name, customer.last_name] if part]
        return " ".join(name_parts) if name_parts else str(customer.id)

    async def __load_order_items(self, order_id: int) -> None:
        if not self._view:
            return
        self.__pending_moves.clear()
        self.__package_pending_moves.clear()
        order_items = await self.__perform_get_order_items(order_id)
        if not order_items:
            self.__order_items = {}
            self.__order_items_by_item = {}
            self.__order_item_quantities = {}
            self.__order_item_original_quantities = {}
            self.__order_item_labels = {}
            self.__items_by_id = {}
            self.__saved_target_rows = []
            self.__target_rows = []
            self.__package_saved_target_rows = []
            self.__package_target_rows = []
            self._view.set_source_rows([])
            self._view.set_source_enabled(False)
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            self.__refresh_package_source_rows()
            self._view.set_package_target_rows([])
            self._view.set_package_target_enabled(False)
            self._view.set_complete_button_enabled(False)
            return
        self.__order_items = {item.id: item for item in order_items}
        self.__order_items_by_item = {}
        self.__order_item_quantities = {}
        self.__order_item_original_quantities = {}
        item_ids = [item.item_id for item in order_items]
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        self.__items_by_id = item_map
        self.__order_item_labels = {}
        for item in order_items:
            item_schema = item_map.get(item.item_id)
            if item_schema:
                self.__order_item_labels[item.item_id] = (item_schema.index, item_schema.name)
            else:
                self.__order_item_labels[item.item_id] = (str(item.item_id), "")
            if not item_schema or item_schema.is_package:
                continue
            if item.to_process > 0:
                self.__order_items_by_item.setdefault(item.item_id, []).append(item)
                self.__order_item_quantities[item.item_id] = (
                    self.__order_item_quantities.get(item.item_id, 0) + item.to_process
                )
                self.__order_item_original_quantities[item.item_id] = (
                    self.__order_item_original_quantities.get(item.item_id, 0) + item.to_process
                )
        bin_ids = list({item.bin_id for item in order_items if item.bin_id is not None})
        bin_locations: dict[int, str] = {}
        if bin_ids:
            bins = await self.__perform_get_bins_by_ids(bin_ids)
            bin_locations = {bin.id: bin.location for bin in bins}
        normal_items: list[AssocOrderItemPlainSchema] = []
        package_items: list[AssocOrderItemPlainSchema] = []
        for item in order_items:
            item_schema = item_map.get(item.item_id)
            if item_schema and item_schema.is_package:
                package_items.append(item)
            else:
                normal_items.append(item)
        self.__saved_target_rows = self.__build_saved_target_rows(normal_items, bin_locations)
        self.__package_saved_target_rows = self.__build_package_saved_target_rows(package_items, bin_locations)
        self.__refresh_source_rows()
        self.__refresh_target_rows()
        self._view.set_target_rows(self.__target_rows)
        self._view.set_target_enabled(bool(self.__target_rows))
        self.__refresh_package_source_rows()
        self.__refresh_package_target_rows()
        self._view.set_package_target_rows(self.__package_target_rows)
        self._view.set_package_target_enabled(bool(self.__package_target_rows))
        self.__update_package_transfer_state()
        self.__update_complete_button_state()
        self.__sync_transfer_state()

    def __build_saved_target_rows(
        self, order_items: list[AssocOrderItemPlainSchema], bin_locations: dict[int, str]
    ) -> list[tuple[int, list[Any]]]:
        rows: list[tuple[int, list[Any]]] = []
        for order_item in order_items:
            if order_item.bin_id is None:
                continue
            picked_quantity = max(order_item.quantity - order_item.to_process, 0)
            if picked_quantity <= 0:
                continue
            index, name = self.__order_item_labels.get(order_item.item_id, (str(order_item.item_id), ""))
            location = bin_locations.get(order_item.bin_id, "")
            rows.append((order_item.id, [index, name, location, str(picked_quantity)]))
        return rows

    def __build_package_saved_target_rows(
        self, order_items: list[AssocOrderItemPlainSchema], bin_locations: dict[int, str]
    ) -> list[tuple[int, list[Any]]]:
        rows: list[tuple[int, list[Any]]] = []
        for order_item in order_items:
            if order_item.bin_id is None:
                continue
            picked_quantity = max(order_item.quantity - order_item.to_process, 0)
            if picked_quantity <= 0:
                continue
            index, name = self.__order_item_labels.get(order_item.item_id, (str(order_item.item_id), ""))
            location = bin_locations.get(order_item.bin_id, "")
            rows.append((order_item.id, [index, name, location, str(picked_quantity)]))
        return rows

    def __sync_transfer_state(self) -> None:
        if not self._view:
            return
        source_enabled = any(quantity > 0 for quantity in self.__order_item_quantities.values())
        target_enabled = source_enabled
        self._view.set_source_enabled(source_enabled)
        self._view.set_target_enabled(target_enabled)

    async def __handle_move_with_quantity(self, item_id: int, max_quantity: int) -> None:
        if not self._view:
            return
        bin_item_schemas = await self.__perform_get_bin_items_for_item(item_id)
        if not bin_item_schemas:
            return
        bin_ids = list({item.bin_id for item in bin_item_schemas})
        bins = await self.__perform_get_bins_by_ids(bin_ids)
        bin_map = {bin.id: bin for bin in bins if bin.is_outbound}
        order_rows = self.__order_items_by_item.get(item_id, [])
        sum_without_bin = sum(row.to_process for row in order_rows if row.bin_id is None)
        sum_by_bin: dict[int, int] = {}
        for row in order_rows:
            if row.bin_id is None:
                continue
            sum_by_bin[row.bin_id] = sum_by_bin.get(row.bin_id, 0) + row.to_process
        pending_total = sum(
            qty for pending_item, _, _, _, qty, _, _ in self.__pending_moves.values() if pending_item == item_id
        )
        pending_by_bin: dict[int, int] = {}
        for pending_item, _, pending_bin_id, _, qty, _, _ in self.__pending_moves.values():
            if pending_item != item_id:
                continue
            pending_by_bin[pending_bin_id] = pending_by_bin.get(pending_bin_id, 0) + qty
        bin_specific_used = 0
        for bin_id, to_process in sum_by_bin.items():
            bin_specific_used += min(to_process, pending_by_bin.get(bin_id, 0))
        pending_unassigned = max(0, pending_total - bin_specific_used)
        remaining_unassigned = max(0, sum_without_bin - pending_unassigned)
        bin_items: list[tuple[int, int, str, int, int]] = []
        for bin_item in bin_item_schemas:
            bin_schema = bin_map.get(bin_item.bin_id)
            if not bin_schema:
                continue
            available_from_bin = max(0, sum_by_bin.get(bin_item.bin_id, 0) - pending_by_bin.get(bin_item.bin_id, 0))
            available_for_bin = available_from_bin + remaining_unassigned
            available_stock = max(0, bin_item.quantity - pending_by_bin.get(bin_item.bin_id, 0))
            effective_available = min(available_for_bin, available_stock)
            if effective_available <= 0:
                continue
            bin_items.append(
                (bin_item.id, bin_item.bin_id, bin_schema.location, effective_available, bin_item.quantity)
            )
        if not bin_items:
            return
        default_quantity = min(
            max_quantity,
            max((quantity for _, _, _, quantity, _ in bin_items), default=0),
        )
        if default_quantity <= 0:
            return
        dialog = BinQuantityDialogComponent(
            self._state_store.app_state.translation.items,
            [(bin_id, location, quantity) for _, bin_id, location, quantity, _ in bin_items],
            default_quantity,
            max_quantity,
        )
        try:
            await self._show_dialog_serialized(dialog, wait_for_future=dialog.future)
            result = await dialog.future
        finally:
            self._page.pop_dialog()
        if not result:
            return
        bin_id, quantity = result
        bin_item = next((item for item in bin_items if item[1] == bin_id), None)
        if not bin_item:
            return
        bin_item_id, bin_id, location, max_allowed, bin_item_quantity = bin_item
        quantity = min(quantity, max_allowed, max_quantity)
        if quantity <= 0:
            return
        index, name = self.__order_item_labels.get(item_id, (str(item_id), ""))
        existing_target_id = next(
            (
                target_id
                for target_id, (_, existing_bin_item_id, _, _, _, _, _) in self.__pending_moves.items()
                if existing_bin_item_id == bin_item_id
            ),
            None,
        )
        if existing_target_id is not None:
            existing = self.__pending_moves[existing_target_id]
            new_quantity = min(existing[4] + quantity, existing[3])
            self.__pending_moves[existing_target_id] = (
                item_id,
                bin_item_id,
                existing[2],
                existing[3],
                new_quantity,
                location,
                existing[6],
            )
            self._view.update_existing_target(existing_target_id, item_id, [index, name, location, str(new_quantity)])
        else:
            target_id = self._view.add_target_row(item_id, [index, name, location, str(quantity)])
            self.__pending_moves[target_id] = (
                item_id,
                bin_item_id,
                bin_id,
                max_allowed,
                quantity,
                location,
                bin_item_quantity,
            )
        self.__refresh_source_rows()
        self.__refresh_target_rows()

    async def __handle_package_move_with_quantity(self, item_id: int, max_quantity: int) -> None:
        if not self._view:
            return
        item_schema = self.__package_items_by_id.get(item_id)
        if not item_schema:
            return
        bin_item_schemas = await self.__perform_get_bin_items_for_item(item_id)
        if not bin_item_schemas:
            return
        bin_ids = list({item.bin_id for item in bin_item_schemas})
        bins = await self.__perform_get_bins_by_ids(bin_ids)
        bin_map = {bin.id: bin for bin in bins if bin.is_outbound}
        pending_total = sum(
            qty for pending_item, _, _, _, qty, _, _ in self.__package_pending_moves.values() if pending_item == item_id
        )
        pending_by_bin: dict[int, int] = {}
        for pending_item, _, pending_bin_id, _, qty, _, _ in self.__package_pending_moves.values():
            if pending_item != item_id:
                continue
            pending_by_bin[pending_bin_id] = pending_by_bin.get(pending_bin_id, 0) + qty
        remaining_total = max(0, max_quantity - pending_total)
        bin_items: list[tuple[int, int, str, int, int]] = []
        for bin_item in bin_item_schemas:
            bin_schema = bin_map.get(bin_item.bin_id)
            if not bin_schema:
                continue
            available_stock = max(0, bin_item.quantity - pending_by_bin.get(bin_item.bin_id, 0))
            effective_available = min(available_stock, remaining_total)
            if effective_available <= 0:
                continue
            bin_items.append(
                (bin_item.id, bin_item.bin_id, bin_schema.location, effective_available, bin_item.quantity)
            )
        if not bin_items:
            return
        default_quantity = 1
        if default_quantity <= 0:
            return
        dialog = BinQuantityDialogComponent(
            self._state_store.app_state.translation.items,
            [(bin_id, location, quantity) for _, bin_id, location, quantity, _ in bin_items],
            default_quantity,
            max_quantity,
        )
        try:
            await self._show_dialog_serialized(dialog, wait_for_future=dialog.future)
            result = await dialog.future
        finally:
            self._page.pop_dialog()
        if not result:
            return
        bin_id, quantity = result
        bin_item = next((item for item in bin_items if item[1] == bin_id), None)
        if not bin_item:
            return
        bin_item_id, bin_id, location, max_allowed, bin_item_quantity = bin_item
        quantity = min(quantity, max_allowed, max_quantity)
        if quantity <= 0:
            return
        index, name = item_schema.index, item_schema.name
        existing_target_id = next(
            (
                target_id
                for target_id, (_, existing_bin_item_id, _, _, _, _, _) in self.__package_pending_moves.items()
                if existing_bin_item_id == bin_item_id
            ),
            None,
        )
        if existing_target_id is not None:
            existing = self.__package_pending_moves[existing_target_id]
            new_quantity = min(existing[4] + quantity, existing[3])
            self.__package_pending_moves[existing_target_id] = (
                item_id,
                bin_item_id,
                existing[2],
                existing[3],
                new_quantity,
                location,
                existing[6],
            )
            self._view.update_existing_package_target(
                existing_target_id, item_id, [index, name, location, str(new_quantity)]
            )
        else:
            target_id = self._view.add_package_target_row(item_id, [index, name, location, str(quantity)])
            self.__package_pending_moves[target_id] = (
                item_id,
                bin_item_id,
                bin_id,
                max_allowed,
                quantity,
                location,
                bin_item_quantity,
            )
        self.__refresh_package_source_rows()
        self.__refresh_package_target_rows()

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view:
            return
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        updates: list[AssocBinItemStrictSchema] = []
        delete_ids: list[int] = []
        order_item_updates: list[AssocOrderItemStrictSchema] = []
        order_item_creates: list[AssocOrderItemStrictSchema] = []
        touched_item_ids: set[int] = set()
        moved_by_item: dict[int, int] = {}
        moved_by_item_bin: dict[tuple[int, int], int] = {}
        for target_id, _ in pending_targets:
            pending = self.__pending_moves.get(target_id)
            if not pending:
                continue
            item_id, bin_item_id, bin_id, _, quantity, _, bin_item_quantity = pending
            moved_by_item[item_id] = moved_by_item.get(item_id, 0) + quantity
            moved_by_item_bin[(item_id, bin_id)] = moved_by_item_bin.get((item_id, bin_id), 0) + quantity
            touched_item_ids.add(item_id)
            new_quantity = max(0, bin_item_quantity - quantity)
            if new_quantity > 0:
                updates.append(
                    AssocBinItemStrictSchema(
                        id=bin_item_id,
                        bin_id=bin_id,
                        item_id=item_id,
                        quantity=new_quantity,
                    )
                )
            else:
                delete_ids.append(bin_item_id)
        order_item_states: dict[int, dict[str, Any]] = {}
        for order_item in self.__order_items.values():
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
        for (item_id, bin_id), moved_quantity in moved_by_item_bin.items():
            if moved_quantity <= 0:
                continue
            order_rows = self.__order_items_by_item.get(item_id, [])
            if not order_rows:
                continue
            remaining = moved_quantity
            ordered_rows = [row for row in order_rows if row.bin_id == bin_id and row.to_process > 0] + [
                row for row in order_rows if row.bin_id is None and row.to_process > 0
            ]
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
                            bin_id=bin_id,
                            category_discount_id=state["category_discount_id"],
                            customer_discount_id=state["customer_discount_id"],
                            item_discount_id=state["item_discount_id"],
                        )
                    )
                else:
                    state["to_process"] = max(0, to_process - take)
                    if state["to_process"] == 0 and not bin_assigned:
                        state["bin_id"] = bin_id
                remaining -= take
        for order_item in self.__order_items.values():
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
        if updates:
            await self.__perform_update_bin_items(updates)
        if delete_ids:
            await self.__perform_delete_bin_items(delete_ids)
        if order_item_updates:
            await self.__perform_update_order_items(order_item_updates)
        if order_item_creates:
            await self.__perform_create_order_items(order_item_creates)
        if moved_by_item:
            missing_item_ids = [item_id for item_id in moved_by_item if item_id not in self.__items_by_id]
            if missing_item_ids:
                fetched_items = await self.__perform_get_items_by_ids(missing_item_ids)
                for item in fetched_items:
                    self.__items_by_id[item.id] = item
            update_tasks = []
            for item_id, moved_quantity in moved_by_item.items():
                item_schema = self.__items_by_id.get(item_id)
                if not item_schema:
                    continue
                new_stock = max(0, item_schema.stock_quantity - moved_quantity)
                update_tasks.append(
                    self.__perform_update_item(item_id, self.__build_item_update(item_schema, new_stock))
                )
            if update_tasks:
                await asyncio.gather(*update_tasks)
        self.__pending_moves.clear()
        if self.__current_order_id is not None:
            await self.__load_order_items(self.__current_order_id)
            await self.__check_and_update_order_status(self.__current_order_id, touched_item_ids)

    async def __handle_package_save(self) -> None:
        if not self._view or self.__current_order_id is None:
            return
        pending_targets = self._view.get_pending_package_targets()
        if not pending_targets:
            return
        updates: list[AssocBinItemStrictSchema] = []
        delete_ids: list[int] = []
        order_item_creates: list[AssocOrderItemStrictSchema] = []
        moved_by_item: dict[int, int] = {}
        for target_id, _ in pending_targets:
            pending = self.__package_pending_moves.get(target_id)
            if not pending:
                continue
            item_id, bin_item_id, bin_id, _, quantity, _, bin_item_quantity = pending
            moved_by_item[item_id] = moved_by_item.get(item_id, 0) + quantity
            new_quantity = max(0, bin_item_quantity - quantity)
            if new_quantity > 0:
                updates.append(
                    AssocBinItemStrictSchema(
                        id=bin_item_id,
                        bin_id=bin_id,
                        item_id=item_id,
                        quantity=new_quantity,
                    )
                )
            else:
                delete_ids.append(bin_item_id)
            order_item_creates.append(
                AssocOrderItemStrictSchema(
                    order_id=self.__current_order_id,
                    item_id=item_id,
                    quantity=quantity,
                    total_net=0,
                    total_vat=0,
                    total_gross=0,
                    total_discount=0,
                    to_process=0,
                    bin_id=bin_id,
                    category_discount_id=None,
                    customer_discount_id=None,
                    item_discount_id=None,
                )
            )
        if updates:
            await self.__perform_update_bin_items(updates)
        if delete_ids:
            await self.__perform_delete_bin_items(delete_ids)
        if order_item_creates:
            await self.__perform_create_order_items(order_item_creates)
        if moved_by_item:
            update_tasks = []
            for item_id, moved_quantity in moved_by_item.items():
                item_schema = self.__package_items_by_id.get(item_id)
                if not item_schema:
                    continue
                new_stock = max(0, item_schema.stock_quantity - moved_quantity)
                update_tasks.append(
                    self.__perform_update_item(item_id, self.__build_item_update(item_schema, new_stock))
                )
            if update_tasks:
                await asyncio.gather(*update_tasks)
        self.__package_pending_moves.clear()
        await self.__load_order_items(self.__current_order_id)

    async def __handle_complete_status(self) -> None:
        if self.__current_order_id is None:
            return
        statuses = await self.__perform_get_all_statuses()
        final_status = next((status for status in statuses if status.order == 4), None)
        if not final_status:
            return
        order_statuses = await self.__perform_get_order_statuses(self.__current_order_id)
        if order_statuses:
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            if latest_status.status_id == final_status.id:
                return
        await self.__perform_create_order_status(
            AssocOrderStatusStrictSchema(order_id=self.__current_order_id, status_id=final_status.id)
        )
        await self.__load_order_items(self.__current_order_id)

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
        return

    def __refresh_source_rows(self) -> None:
        if not self._view:
            return
        source_rows: list[tuple[int, list[Any]]] = []
        for item_id, quantity in self.__order_item_quantities.items():
            pending_quantity = sum(
                qty for pending_item, _, _, _, qty, _, _ in self.__pending_moves.values() if pending_item == item_id
            )
            remaining = max(0, quantity - pending_quantity)
            if remaining <= 0:
                continue
            index, name = self.__order_item_labels.get(item_id, (str(item_id), ""))
            source_rows.append((item_id, [index, name, str(remaining)]))
        self._view.set_source_rows(source_rows)
        self._view.set_source_enabled(bool(source_rows))
        self.__update_complete_button_state()
        self.__sync_transfer_state()

    def __refresh_target_rows(self) -> None:
        if not self._view:
            return
        self.__target_rows = list(self.__saved_target_rows) + [
            (
                target_id,
                [
                    self.__order_item_labels.get(item_id, (str(item_id), ""))[0],
                    self.__order_item_labels.get(item_id, (str(item_id), ""))[1],
                    location,
                    str(quantity),
                ],
            )
            for target_id, (item_id, _, _, _, quantity, location, _) in self.__pending_moves.items()
        ]
        self.__sync_transfer_state()

    def __refresh_package_source_rows(self) -> None:
        if not self._view:
            return
        source_rows: list[tuple[int, list[Any]]] = []
        for item_id, quantity in self.__package_item_quantities.items():
            pending_quantity = sum(
                qty
                for pending_item, _, _, _, qty, _, _ in self.__package_pending_moves.values()
                if pending_item == item_id
            )
            remaining = max(0, quantity - pending_quantity)
            if remaining <= 0:
                continue
            item = self.__package_items_by_id.get(item_id)
            if not item:
                continue
            source_rows.append((item_id, [item.index, item.name, str(remaining)]))
        self._view.set_package_source_rows(source_rows)
        self._view.set_package_source_enabled(bool(source_rows))
        self.__update_package_transfer_state()
        self.__update_complete_button_state()

    def __refresh_package_target_rows(self) -> None:
        if not self._view:
            return
        if self.__package_pending_moves:
            has_targets = bool(self.__package_saved_target_rows) or bool(self.__package_pending_moves)
            self._view.set_package_target_enabled(has_targets)
            self.__update_complete_button_state()
            return
        self.__package_target_rows = list(self.__package_saved_target_rows)
        self._view.set_package_target_rows(self.__package_target_rows)
        self._view.set_package_target_enabled(bool(self.__package_target_rows))
        self.__update_complete_button_state()

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
