from datetime import date
from typing import Any
import math
import random
import string

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, SalesOrderStrictSchema
from pydantic import ValidationError
from schemas.business.trade.order_view_schema import (
    OrderViewResponseSchema,
    OrderViewExchangeRateSchema,
    OrderViewDiscountSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewTargetItemSchema,
)
from services.base.base_service import BaseService
from services.business.logistic import ItemService
from schemas.business.logistic.item_schema import ItemPlainSchema
from services.business.trade import AssocOrderItemService, AssocOrderStatusService, OrderService, OrderViewService
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from events.events import ViewRequested
from views.business.trade.sales_order_view import SalesOrderView
from views.components.quantity_dialog_component import QuantityDialogComponent


class SalesOrderController(BaseViewController[OrderService, SalesOrderView, OrderPlainSchema, SalesOrderStrictSchema]):
    _plain_schema_cls = OrderPlainSchema
    _strict_schema_cls = SalesOrderStrictSchema
    _service_cls = OrderService
    _view_cls = SalesOrderView
    _endpoint = Endpoint.ORDERS
    _view_key = View.SALES_ORDERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_view_service = OrderViewService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__order_items: dict[int, tuple[int, int]] = {}
        self.__order_item_by_item_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__source_item_rows: dict[int, list[str]] = {}
        self.__source_item_category_map: dict[int, int | None] = {}
        self.__item_stock_map: dict[int, tuple[int, int, int]] = {}
        self.__item_dimensions: dict[int, tuple[float, float, float, float]] = {}
        self.__delivery_method_map: dict[int, tuple[float, float, float, float, float, int | None]] = {}
        self.__exchange_rate_map: dict[tuple[int, int], float] = {}
        self.__item_currency_map: dict[int, int] = {}
        self.__exchange_rate_missing_notified = False
        self.__item_pricing: dict[int, tuple[float, float]] = {}
        self.__customer_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__category_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__item_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__discount_percent_map: dict[int, float] = {}
        self.__selected_customer_discount_id: int | None = None
        self.__selected_category_discount_id: int | None = None
        self.__selected_category_id: int | None = None
        self.__selected_item_discount_ids: dict[int, int | None] = {}
        self.__default_status_id: int | None = None
        self.__current_status_id: int | None = None

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> SalesOrderView:
        order_id = event.data.get("id") if event.data else None
        view_data = await self.__perform_get_sales_view(order_id)
        customers = [(item.id, item.label) for item in view_data.customers]
        currencies = [(item.id, item.label) for item in view_data.currencies]
        categories = [(item.id, item.label) for item in view_data.categories]
        self.__delivery_method_map = {
            item.id: (
                item.price_per_unit,
                item.max_width,
                item.max_height,
                item.max_length,
                item.max_weight,
                item.carrier_currency_id,
            )
            for item in view_data.delivery_methods
        }
        self.__load_exchange_rates(view_data.exchange_rates)
        delivery_methods = [(item.id, item.label) for item in view_data.delivery_methods]
        statuses = [(item.id, translation.get(item.label)) for item in view_data.statuses]
        status_steps = {item.id: item.status_number for item in view_data.statuses}
        self.__customer_discount_map = {item.id: item.discounts for item in view_data.customers}
        self.__category_discount_map = {item.id: item.discounts for item in view_data.categories}
        self.__item_discount_map = {item.id: item.discounts for item in view_data.source_items}
        self.__discount_percent_map = {}
        for discounts in (
            self.__customer_discount_map.values(),
            self.__category_discount_map.values(),
            self.__item_discount_map.values(),
        ):
            for discount_list in discounts:
                for discount in discount_list:
                    if discount.percent is not None:
                        self.__discount_percent_map[discount.id] = discount.percent
        self.__order_items = {}
        self.__order_item_by_item_id = {}
        self.__pending_move_quantities.clear()
        self.__source_item_rows.clear()
        self.__source_item_category_map.clear()
        self.__item_stock_map.clear()
        self.__item_dimensions.clear()
        self.__item_currency_map.clear()
        self.__item_pricing.clear()
        self.__current_status_id = None
        self.__exchange_rate_missing_notified = False
        self.__selected_customer_discount_id = None
        self.__selected_category_discount_id = None
        self.__selected_category_id = None
        self.__selected_item_discount_ids.clear()
        default_status = next((item for item in view_data.statuses if item.status_number == 1), None)
        self.__default_status_id = default_status.id if default_status else None
        source_items, source_item_categories = self.__build_source_item_rows(view_data.source_items)
        target_items = self.__build_target_item_rows(view_data.target_items)
        status_history = self.__build_status_history(view_data.status_history)
        order_data = event.data
        if view_data.order:
            order_data = view_data.order.model_dump()
        if mode in {ViewMode.READ, ViewMode.EDIT} and order_data:
            current_status_id = self.__get_latest_status_id(view_data.status_history)
            if current_status_id is None:
                current_status_id = self.__default_status_id
            if current_status_id is not None:
                order_data["status_id"] = current_status_id
                self.__current_status_id = current_status_id
        bulk_transfer_enabled = False
        if mode == ViewMode.READ:
            bulk_transfer_enabled = self.__is_bulk_transfer_enabled(self.__current_status_id, status_steps)
        view = SalesOrderView(
            self,
            translation,
            mode,
            event.view_key,
            order_data,
            customers,
            currencies,
            statuses,
            delivery_methods,
            categories,
            source_items,
            source_item_categories,
            self.__customer_discount_map,
            self.__category_discount_map,
            self.__item_discount_map,
            self.__selected_item_discount_ids,
            target_items,
            status_history,
            bulk_transfer_enabled,
            self.on_order_items_save_clicked,
            self.on_order_items_move_requested,
            self.on_order_items_delete_clicked,
            self.on_order_items_pending_reverted,
        )
        if mode in {ViewMode.READ, ViewMode.EDIT}:
            if order_data:
                view.set_order_totals(
                    order_data.get("total_net", 0.0),
                    order_data.get("total_vat", 0.0),
                    order_data.get("total_gross", 0.0),
                    order_data.get("total_discount", 0.0),
                )
        return view

    def on_order_items_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_order_items_save)

    def on_order_items_move_requested(self, selected_ids: list[int]) -> None:
        if not self._view or not selected_ids:
            return
        item_id = selected_ids[0]
        self._page.run_task(self.__handle_move_with_quantity, item_id)

    def on_order_items_delete_clicked(self, item_ids: list[int]) -> None:
        if not self._view or not item_ids:
            return
        self._page.run_task(self.__handle_order_items_delete, item_ids)

    def on_order_items_pending_reverted(self, target_ids: list[int]) -> None:
        for target_id in target_ids:
            self.__pending_move_quantities.pop(target_id, None)
        self.__recalculate_order_totals()

    async def _perform_get_page(
        self, service: BaseService[OrderPlainSchema, SalesOrderStrictSchema], endpoint: Endpoint
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        return await super()._perform_get_page(service, Endpoint.SALES_ORDERS)

    def get_create_defaults(self) -> dict[str, object]:
        return self.__build_create_defaults()

    def set_hidden_field_value(self, key: str, value: object) -> None:
        self._request_data.input_values[key] = value

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        if key == "is_sales":
            value = True
        super().set_field_value(key, value)
        if key == "delivery_method_id":
            self.__recalculate_shipping_cost()
        if key == "currency_id":
            self.__recalculate_order_totals()

    def set_customer_discount_id(self, discount_id: int | None) -> None:
        self.__selected_customer_discount_id = discount_id
        self.__recalculate_order_totals()

    def set_category_discount_id(self, category_id: int | None, discount_id: int | None) -> None:
        self.__selected_category_id = category_id
        self.__selected_category_discount_id = discount_id
        self.__recalculate_order_totals()

    def set_selected_category_id(self, category_id: int | None) -> None:
        self.__selected_category_id = category_id
        if self.__selected_category_discount_id is not None and category_id is None:
            self.__selected_category_discount_id = None
        self.__recalculate_order_totals()

    def set_item_discount_id(self, item_id: int, discount_id: int | None) -> None:
        self.__selected_item_discount_ids[item_id] = discount_id
        self.__recalculate_order_totals()

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_view(self, order_id: int | None) -> OrderViewResponseSchema:
        return await self.__order_view_service.get_view(
            Endpoint.ORDER_VIEW_SALES, order_id, None, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_by_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        if not item_ids:
            return []
        body_params = IdsPayloadSchema(ids=item_ids)
        items = await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)
        for item in items:
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
        return items

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.create_bulk(
            Endpoint.ORDER_ITEMS_CREATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.update_bulk(
            Endpoint.ORDER_ITEMS_UPDATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_order_items(self, assoc_ids: list[int]) -> None:
        body_params = IdsPayloadSchema(ids=assoc_ids)
        await self.__order_item_service.delete_bulk(
            Endpoint.ORDER_ITEMS_DELETE_BULK, None, None, body_params, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_status(self, payload: AssocOrderStatusStrictSchema) -> None:
        await self.__order_status_service.create(Endpoint.ORDER_STATUSES, None, None, payload, self._module_id)

    def __is_bulk_transfer_enabled(self, status_id: int | None, status_steps: dict[int, int | None]) -> bool:
        if status_id is None or not status_steps:
            return False
        current_step = status_steps.get(status_id)
        if current_step is None:
            return False
        return current_step == 1

    async def __ensure_item_pricing(self, item_ids: list[int]) -> None:
        missing_ids = [item_id for item_id in item_ids if item_id not in self.__item_pricing]
        if missing_ids:
            await self.__perform_get_items_by_ids(missing_ids)

    def __build_source_item_rows(
        self, items: list[OrderViewSourceItemSchema]
    ) -> tuple[list[tuple[int, list[str]]], dict[int, int | None]]:
        results: list[tuple[int, list[str]]] = []
        category_map: dict[int, int | None] = {}
        for item in items:
            if item.is_package:
                continue
            row = [item.index, item.name, str(item.stock_quantity), str(item.reserved_quantity)]
            self.__source_item_rows[item.id] = row
            category_map[item.id] = item.category_id
            self.__item_stock_map[item.id] = (item.stock_quantity, item.reserved_quantity, item.moq)
            self.__item_dimensions[item.id] = (item.width, item.height, item.length, item.weight)
            self.__item_currency_map[item.id] = item.supplier_currency_id
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
            self.__selected_item_discount_ids.setdefault(item.id, None)
            results.append((item.id, row))
        self.__source_item_category_map = category_map
        return results, category_map

    def __build_target_item_rows(self, items: list[OrderViewTargetItemSchema]) -> list[tuple[int, list[str]]]:
        self.__order_items = {item.id: (item.item_id, item.quantity) for item in items}
        self.__order_item_by_item_id = {item.item_id: item.id for item in items}
        results: list[tuple[int, list[str]]] = []
        for item in items:
            row = [item.index, item.name, str(item.quantity)]
            self.__item_dimensions[item.item_id] = (item.width, item.height, item.length, item.weight)
            self.__item_pricing[item.item_id] = (item.purchase_price, item.vat_rate)
            self.__selected_item_discount_ids[item.item_id] = item.discount_id
            results.append((item.id, row))
        return results

    def __build_status_history(self, order_statuses: list[OrderViewStatusHistorySchema]) -> list[dict[str, Any]]:
        translation = self._state_store.app_state.translation.items
        rows: list[dict[str, Any]] = []
        for status in sorted(order_statuses, key=lambda item: item.created_at):
            rows.append(
                {
                    "status": translation.get(status.key),
                    "created_at": self._format_datetime(status.created_at),
                }
            )
        return rows

    def __calculate_item_totals(self, item_id: int, quantity: int) -> tuple[float, float, float, float]:
        purchase_price, vat_rate = self.__item_pricing.get(item_id, (0.0, 0.0))
        purchase_price = self.__convert_to_order_currency(purchase_price, self.__item_currency_map.get(item_id))
        base_net = purchase_price * quantity
        discount_percent = self.__get_discount_percent(item_id)
        total_discount = round(base_net * (discount_percent / 100.0), 2) if discount_percent else 0.0
        total_net = round(base_net - total_discount, 2)
        total_vat = round(total_net * vat_rate, 2)
        total_gross = round(total_net + total_vat, 2)
        return total_net, total_vat, total_gross, total_discount

    def __get_discount_percent(self, item_id: int) -> float:
        discount_id = self.__get_discount_id_for_item(item_id)
        if discount_id is None:
            return 0.0
        return self.__discount_percent_map.get(discount_id, 0.0)

    def __get_discount_id_for_item(self, item_id: int) -> int | None:
        item_discount_id = self.__selected_item_discount_ids.get(item_id)
        if item_discount_id and self.__is_discount_allowed(self.__item_discount_map.get(item_id, []), item_discount_id):
            return item_discount_id

        category_id = self.__source_item_category_map.get(item_id)
        if (
            self.__selected_category_id is not None
            and self.__selected_category_discount_id
            and category_id == self.__selected_category_id
            and self.__is_discount_allowed(
                self.__category_discount_map.get(self.__selected_category_id, []),
                self.__selected_category_discount_id,
            )
        ):
            return self.__selected_category_discount_id

        if self.__selected_customer_discount_id and self.__is_discount_allowed(
            self.__customer_discount_map.get(self.__request_customer_id(), []),
            self.__selected_customer_discount_id,
        ):
            return self.__selected_customer_discount_id

        return None

    @staticmethod
    def __is_discount_allowed(discounts: list[OrderViewDiscountSchema], discount_id: int) -> bool:
        return any(discount.id == discount_id for discount in discounts)

    def __request_customer_id(self) -> int | None:
        customer_id = self._request_data.input_values.get("customer_id")
        return customer_id if isinstance(customer_id, int) else None

    def __compute_order_totals(self, pending_targets: list[tuple[int, int]]) -> tuple[float, float, float, float]:
        pending_by_target = {target_id: item_id for target_id, item_id in pending_targets}
        pending_new_ids = [target_id for target_id in pending_by_target if target_id not in self.__order_items]

        total_net = 0.0
        total_vat = 0.0
        total_gross = 0.0
        total_discount = 0.0

        for target_id, (item_id, base_quantity) in self.__order_items.items():
            pending_quantity = self.__pending_move_quantities.get(target_id, 0)
            quantity = base_quantity + pending_quantity
            net, vat, gross, discount = self.__calculate_item_totals(item_id, quantity)
            total_net += net
            total_vat += vat
            total_gross += gross
            total_discount += discount

        for target_id in pending_new_ids:
            item_id = pending_by_target[target_id]
            quantity = self.__pending_move_quantities.get(target_id, 0)
            net, vat, gross, discount = self.__calculate_item_totals(item_id, quantity)
            total_net += net
            total_vat += vat
            total_gross += gross
            total_discount += discount

        return (
            round(total_net, 2),
            round(total_vat, 2),
            round(total_gross, 2),
            round(total_discount, 2),
        )

    def __recalculate_order_totals(self) -> None:
        if not self._view:
            return
        pending_targets = self._view.get_pending_targets()
        totals = self.__compute_order_totals(pending_targets)
        self._view.set_order_totals(*totals)
        self.__recalculate_shipping_cost(pending_targets)

    def __recalculate_shipping_cost(self, pending_targets: list[tuple[int, int]] | None = None) -> None:
        if not self._view:
            return
        if pending_targets is None:
            pending_targets = self._view.get_pending_targets()
        shipping_cost = self.__compute_shipping_cost(pending_targets)
        self._view.set_shipping_cost(shipping_cost)

    def __compute_shipping_cost(self, pending_targets: list[tuple[int, int]]) -> float:
        delivery_method_id = self._request_data.input_values.get("delivery_method_id")
        if not isinstance(delivery_method_id, int):
            return 0.0
        delivery_method = self.__delivery_method_map.get(delivery_method_id)
        if not delivery_method:
            return 0.0

        price_per_unit, max_width, max_height, max_length, max_weight, carrier_currency_id = delivery_method
        pending_by_target = {target_id: item_id for target_id, item_id in pending_targets}
        pending_new_ids = [target_id for target_id in pending_by_target if target_id not in self.__order_items]

        total_width = 0.0
        total_height = 0.0
        total_length = 0.0
        total_weight = 0.0
        has_items = False

        for target_id, (item_id, base_quantity) in self.__order_items.items():
            pending_quantity = self.__pending_move_quantities.get(target_id, 0)
            quantity = base_quantity + pending_quantity
            if quantity <= 0:
                continue
            dimensions = self.__item_dimensions.get(item_id)
            if not dimensions:
                continue
            width, height, length, weight = dimensions
            total_width += width * quantity
            total_height += height * quantity
            total_length += length * quantity
            total_weight += weight * quantity
            has_items = True

        for target_id in pending_new_ids:
            item_id = pending_by_target[target_id]
            quantity = self.__pending_move_quantities.get(target_id, 0)
            if quantity <= 0:
                continue
            dimensions = self.__item_dimensions.get(item_id)
            if not dimensions:
                continue
            width, height, length, weight = dimensions
            total_width += width * quantity
            total_height += height * quantity
            total_length += length * quantity
            total_weight += weight * quantity
            has_items = True

        if not has_items:
            return 0.0

        units = 1
        max_dimension_sum = max_width + max_height + max_length
        total_dimension_sum = total_width + total_height + total_length
        if max_dimension_sum > 0:
            units = max(units, math.ceil(total_dimension_sum / max_dimension_sum))
        if max_weight > 0:
            units = max(units, math.ceil(total_weight / max_weight))

        cost = price_per_unit * units
        cost = self.__convert_to_order_currency(cost, carrier_currency_id)
        return round(cost, 2)

    def __convert_to_order_currency(self, amount: float, source_currency_id: int | None) -> float:
        order_currency_id = self._request_data.input_values.get("currency_id")
        if not isinstance(order_currency_id, int) or not source_currency_id:
            return amount
        if source_currency_id == order_currency_id:
            return amount
        rate = self.__exchange_rate_map.get((source_currency_id, order_currency_id))
        if rate is None:
            return amount
        return amount * rate

    def __load_exchange_rates(self, exchange_rates: list[OrderViewExchangeRateSchema] | None) -> None:
        self.__exchange_rate_map = {}
        if not exchange_rates:
            self.__notify_missing_exchange_rate()
            return
        missing_rate = False
        for rate in exchange_rates:
            if rate.rate is None:
                missing_rate = True
                continue
            self.__exchange_rate_map[(rate.base_currency_id, rate.quote_currency_id)] = rate.rate
        if missing_rate:
            self.__notify_missing_exchange_rate()

    def __notify_missing_exchange_rate(self) -> None:
        if self.__exchange_rate_missing_notified:
            return
        self.__exchange_rate_missing_notified = True
        self._open_error_dialog(message="Missing exchange rate for currency conversion.")

    async def __handle_move_with_quantity(self, item_id: int) -> None:
        if not self._view:
            return
        await self.__ensure_item_pricing([item_id])
        quantity = await self.__show_quantity_dialog(item_id)
        if quantity is None:
            return
        row = self.__source_item_rows.get(item_id, [str(item_id), "", ""])
        existing_target_id = self.__order_item_by_item_id.get(item_id)
        if existing_target_id is not None:
            base_quantity = self.__order_items[existing_target_id][1]
            pending_quantity = self.__pending_move_quantities.get(existing_target_id, 0)
            new_pending = pending_quantity + quantity
            total_quantity = base_quantity + new_pending
            target_row = [row[0], row[1], str(total_quantity)]
            self._view.update_existing_target(existing_target_id, item_id, target_row)
            self.__pending_move_quantities[existing_target_id] = new_pending
            self.__recalculate_order_totals()
            return
        target_row = [row[0], row[1], str(quantity)]
        target_id = self._view.add_target_row(item_id, target_row, highlight=True)
        self.__pending_move_quantities[target_id] = quantity
        self.__recalculate_order_totals()

    async def __show_quantity_dialog(self, item_id: int) -> int | None:
        stock_info = self.__item_stock_map.get(item_id)
        moq = 1
        available = 0
        if stock_info:
            stock_quantity, reserved_quantity, moq = stock_info
            moq = max(moq, 1)
            available = max(stock_quantity - reserved_quantity, 0)
        max_value = max(available, 0)
        if max_value < moq:
            return None
        translation = self._state_store.app_state.translation.items
        dialog = QuantityDialogComponent(translation, max_value, default_value=moq, min_value=moq, step=moq)
        self._page.show_dialog(dialog)
        try:
            return await dialog.future
        finally:
            self._page.pop_dialog()

    async def __handle_order_items_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        await self.__ensure_item_pricing([item_id for _, item_id in pending_targets])
        payload: list[AssocOrderItemStrictSchema] = []
        updates: list[AssocOrderItemStrictSchema] = []
        for target_id, item_id in pending_targets:
            quantity = self.__pending_move_quantities.get(target_id, 1)
            discount_id = self.__get_discount_id_for_item(item_id)
            if target_id in self.__order_items:
                base_quantity = self.__order_items[target_id][1]
                total_quantity = base_quantity + quantity
                total_net, total_vat, total_gross, total_discount = self.__calculate_item_totals(
                    item_id, total_quantity
                )
                updates.append(
                    AssocOrderItemStrictSchema(
                        id=target_id,
                        order_id=order_id,
                        item_id=item_id,
                        quantity=total_quantity,
                        to_process=total_quantity,
                        total_net=total_net,
                        total_vat=total_vat,
                        total_gross=total_gross,
                        total_discount=total_discount,
                        discount_id=discount_id,
                    )
                )
            else:
                total_net, total_vat, total_gross, total_discount = self.__calculate_item_totals(item_id, quantity)
                payload.append(
                    AssocOrderItemStrictSchema(
                        order_id=order_id,
                        item_id=item_id,
                        quantity=quantity,
                        to_process=quantity,
                        total_net=total_net,
                        total_vat=total_vat,
                        total_gross=total_gross,
                        total_discount=total_discount,
                        discount_id=discount_id,
                    )
                )
        if not payload and not updates:
            return
        if payload:
            await self.__perform_create_order_items(payload)
        if updates:
            await self.__perform_update_order_items(updates)
        await self.__refresh_order_item_lists(order_id)
        self.__pending_move_quantities.clear()
        self.__recalculate_order_totals()
        await self.__update_order_shipping_cost(order_id)

    async def __handle_order_items_delete(self, item_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        assoc_ids = [item_id for item_id in item_ids if item_id in self.__order_items]
        if not assoc_ids:
            return
        await self.__perform_delete_order_items(assoc_ids)
        await self.__refresh_order_item_lists(order_id)
        await self.__update_order_shipping_cost(order_id)

    async def __refresh_order_item_lists(self, order_id: int) -> None:
        if not self._view:
            return
        view_data = await self.__perform_get_sales_view(order_id)
        self.__delivery_method_map = {
            item.id: (
                item.price_per_unit,
                item.max_width,
                item.max_height,
                item.max_length,
                item.max_weight,
                item.carrier_currency_id,
            )
            for item in view_data.delivery_methods
        }
        self.__load_exchange_rates(view_data.exchange_rates)
        self.__customer_discount_map = {item.id: item.discounts for item in view_data.customers}
        self.__category_discount_map = {item.id: item.discounts for item in view_data.categories}
        self.__item_discount_map = {item.id: item.discounts for item in view_data.source_items}
        self.__discount_percent_map = {}
        for discounts in (
            self.__customer_discount_map.values(),
            self.__category_discount_map.values(),
            self.__item_discount_map.values(),
        ):
            for discount_list in discounts:
                for discount in discount_list:
                    if discount.percent is not None:
                        self.__discount_percent_map[discount.id] = discount.percent
        target_items = self.__build_target_item_rows(view_data.target_items)
        source_items, source_item_categories = self.__build_source_item_rows(view_data.source_items)
        self._view.set_target_rows(target_items)
        self._view.set_source_data(
            source_items,
            source_item_categories,
            self.__item_discount_map,
            self.__selected_item_discount_ids,
        )
        self.__recalculate_order_totals()

    async def __update_order_shipping_cost(self, order_id: int) -> None:
        input_values = dict(self._request_data.input_values)
        input_values["is_sales"] = True
        if input_values.get("shipping_cost") is None:
            return
        try:
            payload = SalesOrderStrictSchema(**input_values)
        except ValidationError:
            return
        await self._perform_update(order_id, self._service, self._endpoint, payload)

    def __build_create_defaults(self) -> dict[str, object]:
        today = date.today()
        date_part = today.strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        number = f"{date_part}{suffix}"
        tracking_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        shipping_cost = 0.0
        defaults: dict[str, object] = {
            "number": number,
            "is_sales": True,
            "currency_id": None,
            "total_net": 0,
            "total_vat": 0,
            "total_gross": 0,
            "total_discount": 0,
            "order_date": today,
            "tracking_number": tracking_number,
            "shipping_cost": shipping_cost,
        }
        if self.__default_status_id is not None:
            defaults["status_id"] = self.__default_status_id
        return defaults

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_create(
        self,
        service: BaseService[OrderPlainSchema, SalesOrderStrictSchema],
        endpoint: Endpoint,
        payload: SalesOrderStrictSchema,
    ) -> OrderPlainSchema:
        payload = payload.model_copy(update={"is_sales": True})
        response = await super()._perform_create(service, endpoint, payload)
        status_id = self._request_data.input_values.get("status_id", self.__default_status_id)
        if status_id is not None:
            await self.__perform_create_order_status(
                AssocOrderStatusStrictSchema(order_id=response.id, status_id=status_id)
            )
        return response

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _perform_update(
        self,
        id: int,
        service: BaseService[OrderPlainSchema, SalesOrderStrictSchema],
        endpoint: Endpoint,
        payload: SalesOrderStrictSchema,
    ) -> OrderPlainSchema:
        payload = payload.model_copy(update={"is_sales": True})
        response = await super()._perform_update(id, service, endpoint, payload)
        status_id = self._request_data.input_values.get("status_id")
        if status_id is not None and status_id != self.__current_status_id:
            await self.__perform_create_order_status(AssocOrderStatusStrictSchema(order_id=id, status_id=status_id))
            self.__current_status_id = status_id
        return response

    @staticmethod
    def __get_latest_status_id(order_statuses: list[OrderViewStatusHistorySchema]) -> int | None:
        if not order_statuses:
            return None
        latest_status = max(order_statuses, key=lambda status: status.created_at)
        return latest_status.status_id
