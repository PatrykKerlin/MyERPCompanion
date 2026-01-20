import asyncio
from typing import Any

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema
from schemas.business.trade.order_schema import OrderPlainSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from services.business.trade import (
    AssocOrderItemService,
    AssocOrderStatusService,
    OrderService,
    StatusService,
)
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.stock_receiving_view import StockReceivingView
from views.components.quantity_dialog_component import QuantityDialogComponent


class StockReceivingController(
    BaseViewController[AssocBinItemService, StockReceivingView, AssocBinItemPlainSchema, AssocBinItemStrictSchema]
):
    _plain_schema_cls = AssocBinItemPlainSchema
    _strict_schema_cls = AssocBinItemStrictSchema
    _service_cls = AssocBinItemService
    _view_cls = StockReceivingView
    _endpoint = Endpoint.BIN_ITEMS
    _view_key = View.STOCK_RECEIVING

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__bin_item_service = self._service
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)

        self.__target_bin: BinPlainSchema | None = None
        self.__orders: list[OrderPlainSchema] = []
        self.__order_items: dict[int, AssocOrderItemPlainSchema] = {}
        self.__order_item_quantities: dict[int, int] = {}
        self.__target_items: dict[int, tuple[str, str, int, int]] = {}
        self.__target_bin_item_by_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__second_highest_step: int | None = None
        self.__target_rows: list[tuple[int, list[str]]] = []

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> StockReceivingView:
        mode = ViewMode.STATIC
        orders = await self.__load_eligible_orders()
        order_pairs = [(order.id, order.number) for order in orders]
        return StockReceivingView(
            self,
            translation,
            mode,
            event.view_key,
            order_pairs,
            self.on_order_changed,
            self.on_target_bin_submit,
            self.on_bulk_transfer_save_clicked,
            self.on_bulk_transfer_move_requested,
            self.on_bulk_transfer_pending_reverted,
        )

    def on_order_changed(self, event: ft.Event[ft.Dropdown]) -> None:
        if not self._view:
            return
        value = event.control.value
        if not value:
            self._view.set_order_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_order_error(None)
        order_id = int(value)
        self._page.run_task(self.__load_order_items, order_id)

    def on_target_bin_submit(self, event: ft.Event[ft.TextField]) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self._page.run_task(self.__load_target_bin, location)

    def on_bulk_transfer_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_bulk_transfer_save)

    def on_bulk_transfer_move_requested(self, selected_ids: list[int]) -> None:
        if not self._view or not selected_ids:
            return
        item_id = selected_ids[0]
        max_quantity = self.__order_item_quantities.get(item_id)
        if not max_quantity:
            return
        self._page.run_task(self.__handle_move_with_quantity, item_id, max_quantity)

    def on_bulk_transfer_pending_reverted(self, target_ids: list[int]) -> None:
        for target_id in target_ids:
            self.__pending_move_quantities.pop(target_id, None)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_purchase_orders(self) -> PaginatedResponseSchema[OrderPlainSchema]:
        return await self.__order_service.get_page(
            Endpoint.PURCHASE_ORDERS, None, {"page": 1, "page_size": 200}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_statuses(self, order_id: int) -> list[AssocOrderStatusPlainSchema]:
        return await self.__order_status_service.get_all(
            Endpoint.ORDER_STATUSES, None, {"order_id": order_id}, None, self._module_id
        )

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
    async def __perform_get_single_bin(self, location: str) -> BinPlainSchema | None:
        response = await self.__bin_service.get_page(
            Endpoint.BINS, None, {"page": 1, "page_size": 2, "location": location}, None, self._module_id
        )
        matches = [bin for bin in response.items if bin.location.lower() == location.lower()]
        if len(matches) == 1:
            return matches[0]
        return None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_bin_items(self, bin_id: int) -> list[AssocBinItemPlainSchema]:
        return await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, {"bin_id": bin_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.create_bulk(Endpoint.BIN_ITEMS_CREATE_BULK, None, None, items, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.update_bulk(Endpoint.BIN_ITEMS_UPDATE_BULK, None, None, items, self._module_id)

    async def __load_eligible_orders(self) -> list[OrderPlainSchema]:
        statuses = await self.__perform_get_all_statuses()
        step_numbers = sorted({status.step_number for status in statuses})
        if len(step_numbers) < 2:
            return []
        self.__second_highest_step = step_numbers[-2]
        response = await self.__perform_get_purchase_orders()
        orders = response.items
        eligible: list[OrderPlainSchema] = []
        for order in orders:
            order_statuses = await self.__perform_get_order_statuses(order.id)
            if not order_statuses:
                continue
            oldest_status = min(order_statuses, key=lambda status: status.created_at)
            status = next((s for s in statuses if s.id == oldest_status.status_id), None)
            if status and status.step_number == self.__second_highest_step:
                eligible.append(order)
        self.__orders = eligible
        return eligible

    async def __load_order_items(self, order_id: int) -> None:
        if not self._view:
            return
        self.__pending_move_quantities.clear()
        order_items = await self.__perform_get_order_items(order_id)
        if not order_items:
            self.__order_items = {}
            self.__order_item_quantities = {}
            self._view.set_source_rows([])
            self._view.set_source_enabled(False)
            return
        self.__order_items = {item.item_id: item for item in order_items}
        self.__order_item_quantities = {item.item_id: item.quantity for item in order_items}
        item_ids = [item.item_id for item in order_items]
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        source_rows: list[tuple[int, list[str]]] = []
        for item in order_items:
            item_schema = item_map.get(item.item_id)
            if item_schema:
                source_rows.append((item.item_id, [item_schema.index, item_schema.name, str(item.quantity)]))
            else:
                source_rows.append((item.item_id, [str(item.item_id), "", str(item.quantity)]))
        self._view.set_source_rows(source_rows)
        self._view.set_source_enabled(True)
        if self.__target_rows:
            self._view.set_target_rows(self.__target_rows)
        self.__sync_transfer_state()

    async def __load_target_bin(self, location: str) -> None:
        if not self._view:
            return
        target_bin = await self.__perform_get_single_bin(location)
        if not target_bin:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("bin_not_found"))
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            return
        self.__target_bin = target_bin
        bin_items = await self.__perform_get_bin_items(target_bin.id)
        item_ids = [item.item_id for item in bin_items]
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        self.__target_items = {}
        self.__target_bin_item_by_id = {}
        target_rows: list[tuple[int, list[str]]] = []
        for bin_item in bin_items:
            item_schema = item_map.get(bin_item.item_id)
            if item_schema:
                label = [item_schema.index, item_schema.name, str(bin_item.quantity)]
            else:
                label = [str(bin_item.item_id), "", str(bin_item.quantity)]
            self.__target_items[bin_item.item_id] = (label[0], label[1], bin_item.id, bin_item.quantity)
            self.__target_bin_item_by_id[bin_item.id] = bin_item.item_id
            target_rows.append((bin_item.id, label))
        self._view.set_target_rows(target_rows)
        self.__target_rows = target_rows
        self._view.set_target_enabled(True)
        self.__sync_transfer_state()

    def __sync_transfer_state(self) -> None:
        if not self._view:
            return
        source_enabled = bool(self.__order_items)
        target_enabled = self.__target_bin is not None
        self._view.set_source_enabled(source_enabled)
        self._view.set_target_enabled(target_enabled)

    async def __handle_move_with_quantity(self, item_id: int, max_quantity: int) -> None:
        if not self._view:
            return
        dialog = QuantityDialogComponent(
            self._state_store.app_state.translation.items,
            max_quantity,
            default_value=max_quantity,
            min_value=1,
        )
        self._page.show_dialog(dialog)
        try:
            quantity = await dialog.future
        finally:
            self._page.pop_dialog()
        if quantity is None:
            return
        target_item = self.__target_items.get(item_id)
        if target_item:
            _, _, bin_item_id, current_quantity = target_item
            new_quantity = current_quantity + quantity
            self._view.update_existing_target(
                bin_item_id,
                item_id,
                [target_item[0], target_item[1], str(new_quantity)],
            )
            self.__pending_move_quantities[bin_item_id] = quantity
            return
        target_id = self._view.add_target_row(item_id, [str(item_id), "", str(quantity)])
        self.__pending_move_quantities[target_id] = quantity

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view or not self.__target_bin:
            return
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        creates: list[AssocBinItemStrictSchema] = []
        updates: list[AssocBinItemStrictSchema] = []
        for target_id, item_id in pending_targets:
            move_quantity = self.__pending_move_quantities.get(target_id, 0)
            if move_quantity <= 0:
                continue
            if target_id in self.__target_bin_item_by_id:
                mapped_item_id = self.__target_bin_item_by_id[target_id]
                target_item = self.__target_items.get(mapped_item_id)
                if not target_item:
                    continue
                _, _, bin_item_id, current_quantity = target_item
                updates.append(
                    AssocBinItemStrictSchema(
                        id=bin_item_id,
                        bin_id=self.__target_bin.id,
                        item_id=mapped_item_id,
                        quantity=current_quantity + move_quantity,
                    )
                )
            else:
                creates.append(
                    AssocBinItemStrictSchema(
                        bin_id=self.__target_bin.id,
                        item_id=item_id,
                        quantity=move_quantity,
                    )
                )
        if creates:
            await self.__perform_create_bin_items(creates)
        if updates:
            await self.__perform_update_bin_items(updates)
        await self.__load_target_bin(self.__target_bin.location)
        self.__pending_move_quantities.clear()
