from __future__ import annotations

import asyncio

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.business.trade.stock_receiving_controller import (
    StockReceivingController as DesktopStockReceivingController,
)
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema
from services.business.trade import OrderService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.mobile.stock_receiving_view import StockReceivingView


class StockReceivingController(DesktopStockReceivingController):
    _view_cls = StockReceivingView
    _view_key = View.STOCK_RECEIVING
    _endpoint = Endpoint.BIN_ITEMS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> StockReceivingView:
        orders = await self.__load_mobile_eligible_orders()
        order_pairs = [(order.id, order.tracking_number or order.number) for order in orders]
        return StockReceivingView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
            orders=order_pairs,
        )

    def on_order_changed(self, value: str | None) -> None:
        if isinstance(self._view, StockReceivingView):
            self._view.clear_pending_rows()
        super().on_order_changed(value)

    def on_target_bin_submit(self, location_value: str) -> None:
        if not self._view:
            return
        location = location_value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self._page.run_task(self._load_target_bin_for_location, location)

    def on_add_clicked(self, item_id: int | None, quantity: int | None) -> None:
        if item_id is None or quantity is None or quantity <= 0:
            self._open_error_dialog(message_key="value_required")
            return
        self._page.run_task(self.__handle_add_with_quantity, item_id, quantity)

    def on_pending_item_removed(self, target_id: int) -> None:
        super().on_bulk_transfer_pending_reverted([target_id])

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__handle_save)

    async def __handle_save(self) -> None:
        await self._save_bulk_transfer()
        await self.__check_and_update_mobile_order_status()
        if isinstance(self._view, StockReceivingView):
            self._view.clear_pending_rows()

    async def __handle_add_with_quantity(self, item_id: int, quantity: int) -> None:
        if not isinstance(self._view, StockReceivingView):
            return
        max_quantity = self._get_remaining_order_item_quantity(item_id)
        if not max_quantity or max_quantity <= 0:
            return
        bounded_quantity = min(quantity, max_quantity)
        if bounded_quantity <= 0:
            return

        await self._ensure_order_item_label(item_id)
        target_item = self._get_target_item(item_id)
        if target_item:
            item_index, item_name, bin_item_id, current_quantity = target_item
            current_pending = self._get_pending_quantity(bin_item_id)
            self._view.update_existing_target(
                bin_item_id,
                item_id,
                [item_index, item_name, str(current_quantity + current_pending + bounded_quantity)],
            )
            self._set_pending_quantity(bin_item_id, current_pending + bounded_quantity)
            self._set_pending_item(bin_item_id, item_id)
        else:
            item_index, item_name = self._get_order_item_label(item_id)
            target_id = self._view.add_target_row(item_id, [item_index, item_name, str(bounded_quantity)])
            self._set_pending_quantity(target_id, self._get_pending_quantity(target_id) + bounded_quantity)
            self._set_pending_item(target_id, item_id)

        self._set_remaining_order_item_quantity(item_id, max_quantity - bounded_quantity)
        self._refresh_source_rows_for_view()

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    async def __load_mobile_eligible_orders(self) -> list[OrderPlainSchema]:
        statuses = await self._get_all_statuses()
        eligible_status_ids = [status.id for status in statuses if status.order < 8]
        if not eligible_status_ids:
            return []

        orders_by_status = await asyncio.gather(
            *(self.__perform_get_purchase_orders_by_status_id(status_id) for status_id in eligible_status_ids)
        )
        unique_orders: dict[int, OrderPlainSchema] = {}
        for orders in orders_by_status:
            for order in orders:
                unique_orders[order.id] = order
        return sorted(unique_orders.values(), key=lambda order: (order.number or ""))

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_purchase_orders_by_status_id(self, status_id: int) -> list[OrderPlainSchema]:
        return await self.__order_service.get_all(
            Endpoint.PURCHASE_ORDERS,
            None,
            {"status_id": status_id},
            None,
            self._module_id,
        )

    async def __check_and_update_mobile_order_status(self) -> None:
        order_id = self._get_current_order_id()
        if order_id is None:
            return

        order_items = await self._get_order_items_for_order(order_id)
        if not order_items or any(item.to_process > 0 for item in order_items):
            return

        statuses = await self._get_all_statuses()
        target_status = next((status for status in statuses if status.order == 8), None)
        if not target_status:
            return

        order_statuses = await self._get_order_statuses_for_order(order_id)
        if order_statuses:
            latest_status = max(order_statuses, key=lambda row: row.created_at)
            if latest_status.status_id == target_status.id:
                return

        await self._create_order_status(AssocOrderStatusStrictSchema(order_id=order_id, status_id=target_status.id))
