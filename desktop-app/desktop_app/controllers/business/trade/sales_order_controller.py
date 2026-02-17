import math
import random
import string
from datetime import date
from typing import Any, Callable

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController, TServicePlainSchema, TServiceStrictSchema
from events.events import ViewRequested
from pydantic import ValidationError
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, SalesOrderStrictSchema
from schemas.business.trade.order_view_schema import (
    OrderViewDiscountSchema,
    OrderViewExchangeRateSchema,
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewTargetItemSchema,
)
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from services.base.base_service import BaseService
from services.business.trade import AssocOrderItemService, AssocOrderStatusService, OrderService, OrderViewService
from utils.discount_context import DiscountContext
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.sales_order_view import SalesOrderView
from views.components.quantity_dialog_component import QuantityDialogComponent


class MissingExchangeRateError(RuntimeError):
    pass


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
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)

        self.__order_items: dict[int, tuple[int, int]] = {}
        self.__order_item_by_item_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}

        self.__source_item_rows: dict[int, list[str]] = {}
        self.__source_item_category_map: dict[int, int | None] = {}
        self.__source_selectable_ids: set[int] = set()
        self.__item_stock_map: dict[int, tuple[int, int]] = {}
        self.__item_dimensions: dict[int, tuple[float, float, float, float]] = {}
        self.__item_pricing: dict[int, tuple[float, float]] = {}
        self.__item_currency_map: dict[int, int | None] = {}
        self.__item_category_map: dict[int, int | None] = {}

        self.__delivery_method_map: dict[int, tuple[float, float, float, float, float, int | None]] = {}
        self.__exchange_rate_map: dict[tuple[int, int], float] = {}
        self.__exchange_rate_missing_notified = False
        self.__status_steps: dict[int, int | None] = {}

        self.__customer_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__category_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__item_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__discount_percent_map: dict[int, float] = {}
        self.__selected_customer_discount_id: int | None = None
        self.__selected_item_discount_ids: dict[int, int | None] = {}
        self.__target_category_discount_ids: dict[int, int | None] = {}
        self.__target_customer_discount_ids: dict[int, int | None] = {}
        self.__pending_category_discount_item_ids: set[int] = set()

        self.__default_status_id: int | None = None
        self.__current_status_id: int | None = None
        self.__prefetched_create_number: str | None = None
        self.__number_request_counter = 0

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

    def on_value_changed(self, event: ft.ControlEvent, key: str, *after_change: Callable[[], None]) -> None:
        super().on_value_changed(event, key, *after_change)
        if key == "order_date" and self._view and self._view.mode == ViewMode.CREATE:
            self._page.run_task(self.__refresh_order_number_for_date)

    def get_create_defaults(self) -> dict[str, Any]:
        return self.__build_create_defaults()

    def set_hidden_field_value(self, key: str, value: Any) -> None:
        self._request_data.input_values[key] = value

    def get_search_result_columns(self, available_fields: list[str]) -> list[str]:
        hidden_fields = {
            "customer_id",
            "currency_id",
            "delivery_method_id",
            "status_id",
            "status_ids",
            "notes",
            "internal_notes",
        }
        return [field for field in available_fields if field not in hidden_fields]

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        if key == "is_sales":
            value = True
        if key == "currency_id" and isinstance(value, str):
            value = value.strip()
            if value in {"", "0"}:
                value = None
            elif value.isdigit():
                value = int(value)
        super().set_field_value(key, value)
        if key == "delivery_method_id":
            self.__recalculate_shipping_cost()
        if key == "currency_id":
            self.__recalculate_order_totals()

    def set_customer_discount_id(self, discount_id: int | None) -> None:
        if not self.__is_customer_discount_editable():
            self.__selected_customer_discount_id = discount_id
            return
        persisted_item_ids = {item_id for _, (item_id, _) in self.__order_items.items()}
        pending_item_ids = set()
        if self._view:
            pending_item_ids.update(item_id for _, item_id in self._view.get_pending_targets())
        all_item_ids = persisted_item_ids | pending_item_ids
        if discount_id == self.__selected_customer_discount_id and all(
            self.__target_customer_discount_ids.get(item_id) == discount_id for item_id in all_item_ids
        ):
            return
        should_auto_save = any(
            self.__target_customer_discount_ids.get(item_id) != discount_id for item_id in persisted_item_ids
        )
        self.__selected_customer_discount_id = discount_id
        for item_id in all_item_ids:
            self.__target_customer_discount_ids[item_id] = discount_id
        self.__recalculate_order_totals()
        if not should_auto_save or not self._view or not self._view.data_row or not self.__order_items:
            return
        order_id = self._view.data_row["id"]
        self._page.run_task(self.__auto_save_customer_discount, order_id)

    def set_item_discount_id(self, item_id: int, discount_id: int | None) -> None:
        self.__selected_item_discount_ids[item_id] = discount_id
        self.__recalculate_order_totals()

    def set_category_discount_for_items(
        self, category_id: int | None, discount_id: int | None, item_ids: list[int]
    ) -> None:
        if category_id is None or not item_ids:
            return
        for item_id in item_ids:
            self.__target_category_discount_ids[item_id] = discount_id
        self.__pending_category_discount_item_ids.update(item_ids)
        self.__recalculate_order_totals()

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
        self.__status_steps = status_steps
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
        self.__source_selectable_ids.clear()
        self.__item_stock_map.clear()
        self.__item_dimensions.clear()
        self.__item_currency_map.clear()
        self.__item_category_map.clear()
        self.__item_pricing.clear()
        self.__current_status_id = None
        self.__exchange_rate_missing_notified = False
        self.__selected_customer_discount_id = None
        self.__selected_item_discount_ids.clear()
        self.__target_category_discount_ids.clear()
        self.__target_customer_discount_ids.clear()
        self.__pending_category_discount_item_ids.clear()
        default_status = next((item for item in view_data.statuses if item.status_number == 1), None)
        self.__default_status_id = default_status.id if default_status else None
        if mode == ViewMode.CREATE:
            self.__prefetched_create_number = await self.__generate_order_number(date.today())
        else:
            self.__prefetched_create_number = None
        source_items, source_item_categories = self.__build_source_item_rows(view_data.source_items)
        available_category_ids = {
            category_id for category_id in source_item_categories.values() if category_id is not None
        }
        categories = [item for item in categories if item[0] in available_category_ids]
        target_items, target_item_ids = self.__build_target_item_rows(view_data.target_items)
        status_history = self.__build_status_history(view_data.status_history)
        order_data = event.data
        if view_data.order:
            order_data = view_data.order.model_dump()
            self._parse_data_row(order_data)
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
        (
            customer_discounts,
            category_discounts,
            item_discounts,
            selected_item_discounts,
        ) = self.__get_filtered_discounts_for_view()
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
            dict(self.__item_category_map),
            customer_discounts,
            category_discounts,
            item_discounts,
            selected_item_discounts,
            target_items,
            target_item_ids,
            dict(self.__target_category_discount_ids),
            status_history,
            bulk_transfer_enabled,
            self.on_order_items_save_clicked,
            self.on_order_items_move_requested,
            self.on_order_items_delete_clicked,
            self.on_order_items_pending_reverted,
        )
        customer_discount_id = self.__resolve_target_customer_discount_selection()
        view.set_selected_customer_discount_id(customer_discount_id)
        if mode in {ViewMode.READ, ViewMode.EDIT} and order_data:
            view.set_order_totals(
                order_data.get("total_net", 0.0),
                order_data.get("total_vat", 0.0),
                order_data.get("total_gross", 0.0),
                order_data.get("total_discount", 0.0),
            )
        return view

    async def _perform_get_page(
        self, service: BaseService[TServicePlainSchema, TServiceStrictSchema], endpoint: Endpoint
    ) -> PaginatedResponseSchema[TServicePlainSchema]:
        return await super()._perform_get_page(service, Endpoint.SALES_ORDERS)

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

    async def __auto_save_customer_discount(self, order_id: int) -> None:
        try:
            context = self.__build_discount_context()
            updates: list[AssocOrderItemStrictSchema] = []
            for assoc_id, (item_id, quantity) in self.__order_items.items():
                updates.append(self.__build_order_item_schema(order_id, item_id, quantity, assoc_id, context))
        except MissingExchangeRateError:
            return
        if updates:
            await self.__perform_update_order_items(updates)
            await self.__update_order(order_id)

    def __build_order_item_schema(
        self,
        order_id: int,
        item_id: int,
        quantity: int,
        assoc_id: int | None,
        context: DiscountContext | None = None,
    ) -> AssocOrderItemStrictSchema:
        if context is None:
            context = self.__build_discount_context()
        purchase_price, _ = self.__item_pricing.get(item_id, (0.0, 0.0))
        purchase_price = self.__convert_to_order_currency(purchase_price, self.__item_currency_map.get(item_id))
        base_net = purchase_price * quantity
        item_discount_id, category_discount_id, customer_discount_id = self.__get_discount_payload(
            item_id, quantity, base_net, context
        )
        total_net, total_vat, total_gross, total_discount = self.__calculate_item_totals(item_id, quantity, context)
        data = {
            "order_id": order_id,
            "item_id": item_id,
            "quantity": quantity,
            "to_process": quantity,
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_discount": total_discount,
            "category_discount_id": category_discount_id,
            "customer_discount_id": customer_discount_id,
            "item_discount_id": item_discount_id,
            "bin_id": None,
        }
        if assoc_id is not None:
            data["id"] = assoc_id
        return AssocOrderItemStrictSchema(**data)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_view(self, order_id: int | None) -> OrderViewResponseSchema:
        return await self.__order_view_service.get_view(
            Endpoint.ORDER_VIEW_SALES, order_id, None, None, self._module_id
        )

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

    def __is_customer_discount_editable(self) -> bool:
        if not self._view or self._view.mode != ViewMode.READ:
            return False
        return self.__is_bulk_transfer_enabled(self.__current_status_id, self.__status_steps)

    def __build_source_item_rows(
        self, items: list[OrderViewSourceItemSchema]
    ) -> tuple[list[tuple[int, list[str]]], dict[int, int | None]]:
        results: list[tuple[int, list[str]]] = []
        category_map: dict[int, int | None] = {}
        selectable_ids: set[int] = set()
        for item in items:
            if item.is_package:
                continue
            if item.outbound_quantity <= 0:
                continue
            available_quantity = max(item.outbound_quantity - item.reserved_quantity, 0)
            row = [item.index, item.name, str(item.outbound_quantity), str(item.reserved_quantity)]
            self.__source_item_rows[item.id] = row
            category_map[item.id] = item.category_id
            self.__item_stock_map[item.id] = (available_quantity, item.moq)
            if available_quantity > 0:
                selectable_ids.add(item.id)
            self.__item_dimensions[item.id] = (item.width, item.height, item.length, item.weight)
            self.__item_currency_map[item.id] = item.supplier_currency_id
            self.__item_category_map[item.id] = item.category_id
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
            self.__selected_item_discount_ids.setdefault(item.id, None)
            results.append((item.id, row))
        self.__source_item_category_map = category_map
        self.__source_selectable_ids = selectable_ids
        return results, category_map

    def __build_target_item_rows(
        self, items: list[OrderViewTargetItemSchema]
    ) -> tuple[list[tuple[int, list[str]]], dict[int, int]]:
        self.__order_items = {item.id: (item.item_id, item.quantity) for item in items}
        self.__order_item_by_item_id = {item.item_id: item.id for item in items}
        results: list[tuple[int, list[str]]] = []
        target_item_ids: dict[int, int] = {}
        for item in items:
            row = [item.index, item.name, str(item.quantity)]
            self.__item_dimensions[item.item_id] = (item.width, item.height, item.length, item.weight)
            self.__item_pricing[item.item_id] = (item.purchase_price, item.vat_rate)
            if item.supplier_currency_id is not None:
                self.__item_currency_map[item.item_id] = item.supplier_currency_id
            if item.category_id is not None:
                self.__item_category_map[item.item_id] = item.category_id
            self.__selected_item_discount_ids[item.item_id] = item.item_discount_id
            self.__target_category_discount_ids[item.item_id] = item.category_discount_id
            self.__target_customer_discount_ids[item.item_id] = item.customer_discount_id
            results.append((item.id, row))
            target_item_ids[item.id] = item.item_id
        return results, target_item_ids

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

    def __calculate_item_totals(
        self, item_id: int, quantity: int, context: DiscountContext | None = None
    ) -> tuple[float, float, float, float]:
        if context is None:
            context = self.__build_discount_context()
        purchase_price, vat_rate = self.__item_pricing.get(item_id, (0.0, 0.0))
        purchase_price = self.__convert_to_order_currency(purchase_price, self.__item_currency_map.get(item_id))
        base_net = purchase_price * quantity
        discount_percent = self.__get_discount_percent(item_id, quantity, base_net, context)
        total_discount = round(base_net * discount_percent, 2) if discount_percent else 0.0
        total_net = round(base_net - total_discount, 2)
        total_vat = round(total_net * vat_rate, 2)
        total_gross = round(total_net + total_vat, 2)
        return total_net, total_vat, total_gross, total_discount

    def __get_discount_percent(self, item_id: int, quantity: int, base_net: float, context: DiscountContext) -> float:
        discount_ids = self.__get_discount_ids_for_item(item_id, quantity, base_net, context)
        if not discount_ids:
            return 0.0
        return sum(self.__discount_percent_map.get(discount_id, 0.0) for discount_id in discount_ids)

    def __get_discount_ids_for_item(
        self, item_id: int, quantity: int, base_net: float, context: DiscountContext
    ) -> list[int]:
        discount_ids: list[int] = []
        item_discount_id = self.__selected_item_discount_ids.get(item_id)
        if item_discount_id and self.__is_discount_allowed(
            self.__item_discount_map.get(item_id, []),
            item_discount_id,
            quantity,
            base_net,
        ):
            discount_ids.append(item_discount_id)

        category_id = self.__item_category_map.get(item_id)
        category_quantity = context.category_quantities.get(category_id or -1, 0)
        category_net = context.category_net_map.get(category_id or -1, 0.0)
        category_discount_id = self.__target_category_discount_ids.get(item_id)
        if (
            category_id is not None
            and category_discount_id
            and self.__is_discount_allowed(
                self.__category_discount_map.get(category_id, []),
                category_discount_id,
                category_quantity,
                category_net,
            )
        ):
            discount_ids.append(category_discount_id)

        customer_id = self.__request_customer_id()
        order_quantity = context.order_quantity
        order_net = context.order_net
        customer_discount_id = (
            self.__selected_customer_discount_id
            if self.__selected_customer_discount_id is not None
            else self.__target_customer_discount_ids.get(item_id)
        )
        if (
            customer_id is not None
            and customer_discount_id
            and self.__is_discount_allowed(
                self.__customer_discount_map.get(customer_id, []),
                customer_discount_id,
                order_quantity,
                order_net,
            )
        ):
            discount_ids.append(customer_discount_id)

        return discount_ids

    def __get_discount_payload(
        self, item_id: int, quantity: int, base_net: float, context: DiscountContext
    ) -> tuple[int | None, int | None, int | None]:
        item_discount_id: int | None = None
        category_discount_id: int | None = None
        customer_discount_id: int | None = None

        selected_item_discount = self.__selected_item_discount_ids.get(item_id)
        if selected_item_discount and self.__is_discount_allowed(
            self.__item_discount_map.get(item_id, []),
            selected_item_discount,
            quantity,
            base_net,
        ):
            item_discount_id = selected_item_discount

        category_id = self.__item_category_map.get(item_id)
        category_quantity = context.category_quantities.get(category_id or -1, 0)
        category_net = context.category_net_map.get(category_id or -1, 0.0)
        selected_category_discount_id = self.__target_category_discount_ids.get(item_id)
        if (
            category_id is not None
            and selected_category_discount_id
            and self.__is_discount_allowed(
                self.__category_discount_map.get(category_id, []),
                selected_category_discount_id,
                category_quantity,
                category_net,
            )
        ):
            category_discount_id = selected_category_discount_id

        customer_id = self.__request_customer_id()
        order_quantity = context.order_quantity
        order_net = context.order_net
        selected_customer_discount_id = (
            self.__selected_customer_discount_id
            if self.__selected_customer_discount_id is not None
            else self.__target_customer_discount_ids.get(item_id)
        )
        if (
            customer_id is not None
            and selected_customer_discount_id
            and self.__is_discount_allowed(
                self.__customer_discount_map.get(customer_id, []),
                selected_customer_discount_id,
                order_quantity,
                order_net,
            )
        ):
            customer_discount_id = selected_customer_discount_id

        return item_discount_id, category_discount_id, customer_discount_id

    def __resolve_target_customer_discount_selection(self) -> int | None:
        if self.__selected_customer_discount_id is not None:
            return self.__selected_customer_discount_id
        return next((value for value in self.__target_customer_discount_ids.values() if value is not None), None)

    def __is_discount_allowed(
        self,
        discounts: list[OrderViewDiscountSchema],
        discount_id: int,
        quantity: int,
        base_net: float,
    ) -> bool:
        discount = next((item for item in discounts if item.id == discount_id), None)
        if not discount:
            return False
        if discount.min_quantity is not None and quantity < discount.min_quantity:
            return False
        if discount.min_value is not None:
            if discount.currency_id is None:
                return False
            min_value = self.__convert_to_order_currency(discount.min_value, discount.currency_id)
            if base_net < min_value:
                return False
        return True

    def __request_customer_id(self) -> int | None:
        customer_id = self._request_data.input_values.get("customer_id")
        return customer_id if isinstance(customer_id, int) else None

    def __build_discount_context(self) -> DiscountContext:
        quantities = self.__get_item_quantity_map()
        base_net_map = self.__get_item_base_net_map(quantities)
        order_quantity = sum(quantities.values())
        order_net = sum(base_net_map.values())

        category_quantities: dict[int, int] = {}
        category_net_map: dict[int, float] = {}
        for item_id, quantity in quantities.items():
            category_id = self.__item_category_map.get(item_id)
            if category_id is None:
                continue
            category_quantities[category_id] = category_quantities.get(category_id, 0) + quantity
            category_net_map[category_id] = category_net_map.get(category_id, 0.0) + base_net_map.get(item_id, 0.0)

        return DiscountContext(
            quantities=quantities,
            base_net_map=base_net_map,
            order_quantity=order_quantity,
            order_net=order_net,
            category_quantities=category_quantities,
            category_net_map=category_net_map,
        )

    def __get_filtered_discounts_for_view(
        self,
    ) -> tuple[
        dict[int, list[OrderViewDiscountSchema]],
        dict[int, list[OrderViewDiscountSchema]],
        dict[int, list[OrderViewDiscountSchema]],
        dict[int, int | None],
    ]:
        try:
            context = self.__build_discount_context()
            quantities = context.quantities
            base_net_map = context.base_net_map

            customer_discounts: dict[int, list[OrderViewDiscountSchema]] = {}
            for customer_id, discounts in self.__customer_discount_map.items():
                customer_discounts[customer_id] = [
                    discount
                    for discount in discounts
                    if self.__discount_meets_requirements(discount, context.order_quantity, context.order_net)
                ]

            category_discounts: dict[int, list[OrderViewDiscountSchema]] = {}
            for category_id, discounts in self.__category_discount_map.items():
                category_discounts[category_id] = [
                    discount
                    for discount in discounts
                    if self.__discount_meets_requirements(
                        discount,
                        context.category_quantities.get(category_id, 0),
                        context.category_net_map.get(category_id, 0.0),
                    )
                ]

            item_discounts: dict[int, list[OrderViewDiscountSchema]] = {}
            for item_id, discounts in self.__item_discount_map.items():
                quantity = quantities.get(item_id, 0)
                base_net = base_net_map.get(item_id, 0.0)
                item_discounts[item_id] = [
                    discount
                    for discount in discounts
                    if self.__discount_meets_requirements(discount, quantity, base_net)
                ]

            selected_item_discounts: dict[int, int | None] = {}
            for item_id, discount_id in self.__selected_item_discount_ids.items():
                if discount_id is None:
                    selected_item_discounts[item_id] = None
                    continue
                allowed_ids = {discount.id for discount in item_discounts.get(item_id, [])}
                selected_item_discounts[item_id] = discount_id if discount_id in allowed_ids else None

            return customer_discounts, category_discounts, item_discounts, selected_item_discounts
        except MissingExchangeRateError:
            return (
                dict(self.__customer_discount_map),
                dict(self.__category_discount_map),
                dict(self.__item_discount_map),
                dict(self.__selected_item_discount_ids),
            )

    def __get_item_quantity_map(self) -> dict[int, int]:
        quantities = {item_id: quantity for _, (item_id, quantity) in self.__order_items.items()}
        if not self._view:
            return quantities
        for target_id, item_id in self._view.get_pending_targets():
            pending_quantity = self.__pending_move_quantities.get(target_id, 0)
            if pending_quantity:
                quantities[item_id] = quantities.get(item_id, 0) + pending_quantity
        return quantities

    def __get_item_base_net_map(self, quantities: dict[int, int]) -> dict[int, float]:
        base_net_map: dict[int, float] = {}
        for item_id, quantity in quantities.items():
            purchase_price, _ = self.__item_pricing.get(item_id, (0.0, 0.0))
            purchase_price = self.__convert_to_order_currency(purchase_price, self.__item_currency_map.get(item_id))
            base_net_map[item_id] = purchase_price * quantity
        return base_net_map

    def __discount_meets_requirements(self, discount: OrderViewDiscountSchema, quantity: int, base_net: float) -> bool:
        if discount.min_quantity is not None and quantity < discount.min_quantity:
            return False
        if discount.min_value is not None:
            if discount.currency_id is None:
                return False
            min_value = self.__convert_to_order_currency(discount.min_value, discount.currency_id)
            if base_net < min_value:
                return False
        return True

    def __compute_order_totals(self, pending_targets: list[tuple[int, int]]) -> tuple[float, float, float, float]:
        context = self.__build_discount_context()
        pending_by_target = dict(pending_targets)
        pending_new_ids = [target_id for target_id in pending_by_target if target_id not in self.__order_items]

        total_net = 0.0
        total_vat = 0.0
        total_gross = 0.0
        total_discount = 0.0

        for target_id, (item_id, base_quantity) in self.__order_items.items():
            pending_quantity = self.__pending_move_quantities.get(target_id, 0)
            quantity = base_quantity + pending_quantity
            net, vat, gross, discount = self.__calculate_item_totals(item_id, quantity, context)
            total_net += net
            total_vat += vat
            total_gross += gross
            total_discount += discount

        for target_id in pending_new_ids:
            item_id = pending_by_target[target_id]
            quantity = self.__pending_move_quantities.get(target_id, 0)
            net, vat, gross, discount = self.__calculate_item_totals(item_id, quantity, context)
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
        try:
            totals = self.__compute_order_totals(pending_targets)
        except MissingExchangeRateError:
            return
        self._view.set_order_totals(*totals)
        self.__recalculate_shipping_cost(pending_targets)

    def __recalculate_shipping_cost(self, pending_targets: list[tuple[int, int]] | None = None) -> None:
        if not self._view:
            return
        if pending_targets is None:
            pending_targets = self._view.get_pending_targets()
        try:
            shipping_cost = self.__compute_shipping_cost(pending_targets)
        except MissingExchangeRateError:
            return
        self._view.set_shipping_cost(shipping_cost)

    def __compute_shipping_cost(self, pending_targets: list[tuple[int, int]]) -> float:
        delivery_method_id = self._request_data.input_values.get("delivery_method_id")
        if not isinstance(delivery_method_id, int):
            return 0.0
        delivery_method = self.__delivery_method_map.get(delivery_method_id)
        if not delivery_method:
            return 0.0

        price_per_unit, max_width, max_height, max_length, max_weight, carrier_currency_id = delivery_method
        pending_by_target = dict(pending_targets)
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
        if rate is not None:
            return amount * rate
        reverse_rate = self.__exchange_rate_map.get((order_currency_id, source_currency_id))
        if reverse_rate:
            return amount / reverse_rate
        self.__notify_missing_exchange_rate()
        raise MissingExchangeRateError(f"Missing exchange rate for {source_currency_id} -> {order_currency_id}.")

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
        self._open_error_dialog(message="missing_exchange_rate")

    async def __handle_move_with_quantity(self, item_id: int) -> None:
        if not self._view:
            return
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
            outbound_quantity, moq = stock_info
            moq = max(moq, 1)
            available = max(outbound_quantity, 0)
        max_value = max(available, 0)
        if max_value < moq:
            return None
        translation = self._state_store.app_state.translation.items
        dialog = QuantityDialogComponent(translation, max_value, default_value=moq, min_value=moq, step=moq)
        try:
            await self._show_dialog_serialized(dialog, wait_for_future=dialog.future)
            return await dialog.future
        finally:
            self._page.pop_dialog()

    async def __handle_order_items_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        pending_targets = self._view.get_pending_targets()
        if not pending_targets and not self.__pending_category_discount_item_ids:
            return
        try:
            context = self.__build_discount_context()
            payload: list[AssocOrderItemStrictSchema] = []
            updates: list[AssocOrderItemStrictSchema] = []
            for target_id, item_id in pending_targets:
                quantity = self.__pending_move_quantities.get(target_id, 1)
                if target_id in self.__order_items:
                    base_quantity = self.__order_items[target_id][1]
                    total_quantity = base_quantity + quantity
                    updates.append(
                        self.__build_order_item_schema(order_id, item_id, total_quantity, target_id, context)
                    )
                else:
                    payload.append(self.__build_order_item_schema(order_id, item_id, quantity, None, context))
            if self.__pending_category_discount_item_ids:
                updated_assoc_ids = {update.id for update in updates if update.id is not None}
                for assoc_id, (item_id, quantity) in self.__order_items.items():
                    if item_id not in self.__pending_category_discount_item_ids or assoc_id in updated_assoc_ids:
                        continue
                    updates.append(self.__build_order_item_schema(order_id, item_id, quantity, assoc_id, context))
        except MissingExchangeRateError:
            return
        if not payload and not updates:
            return
        if payload:
            await self.__perform_create_order_items(payload)
        if updates:
            await self.__perform_update_order_items(updates)
        await self.__refresh_order_item_lists(order_id)
        self.__pending_move_quantities.clear()
        self.__pending_category_discount_item_ids.clear()
        self.__recalculate_order_totals()
        await self.__update_order(order_id, require_shipping_cost=True)

    async def __handle_order_items_delete(self, item_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        assoc_ids = [item_id for item_id in item_ids if item_id in self.__order_items]
        if not assoc_ids:
            return
        await self.__perform_delete_order_items(assoc_ids)
        await self.__refresh_order_item_lists(order_id)
        await self.__update_order(order_id, require_shipping_cost=True)

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
        self.__status_steps = {item.id: item.status_number for item in view_data.statuses}
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
        target_items, target_item_ids = self.__build_target_item_rows(view_data.target_items)
        source_items, source_item_categories = self.__build_source_item_rows(view_data.source_items)
        available_category_ids = {
            category_id for category_id in source_item_categories.values() if category_id is not None
        }
        category_pairs = [(item.id, item.label) for item in view_data.categories if item.id in available_category_ids]
        if category_pairs:
            self._view.update_category_options(category_pairs)
        self._view.set_target_data(target_items, target_item_ids, dict(self.__target_category_discount_ids))
        (
            customer_discounts,
            category_discounts,
            item_discounts,
            selected_item_discounts,
        ) = self.__get_filtered_discounts_for_view()
        self._view.set_source_data(
            source_items,
            dict(self.__item_category_map),
            item_discounts,
            selected_item_discounts,
            set(self.__source_selectable_ids),
        )
        self._view.update_discount_options(customer_discounts, category_discounts)
        customer_discount_id = self.__resolve_target_customer_discount_selection()
        self._view.set_selected_customer_discount_id(customer_discount_id)
        self.__recalculate_order_totals()

    async def __update_order(self, order_id: int, *, require_shipping_cost: bool = False) -> None:
        input_values = dict(self._request_data.input_values)
        input_values["is_sales"] = True
        if require_shipping_cost and input_values.get("shipping_cost") is None:
            return
        try:
            payload = SalesOrderStrictSchema(**input_values)
        except ValidationError:
            return
        await self._perform_update(order_id, self._service, self._endpoint, payload)

    def __build_create_defaults(self) -> dict[str, Any]:
        today = date.today()
        number = self.__prefetched_create_number or self.__format_order_number(today, 1)
        defaults: dict[str, Any] = {
            "number": number,
            "is_sales": True,
            "currency_id": None,
            "total_net": 0,
            "total_vat": 0,
            "total_gross": 0,
            "total_discount": 0,
            "order_date": today,
            "shipping_cost": 0,
        }
        if self.__default_status_id is not None:
            defaults["status_id"] = self.__default_status_id
        return defaults

    async def __refresh_order_number_for_date(self) -> None:
        if not self._view or self._view.mode != ViewMode.CREATE:
            return
        order_date = self._request_data.input_values.get("order_date")
        if isinstance(order_date, str):
            try:
                order_date = date.fromisoformat(order_date)
            except ValueError:
                return
        if not isinstance(order_date, date):
            return
        self.__number_request_counter += 1
        request_id = self.__number_request_counter
        number = await self.__generate_order_number(order_date)
        if request_id != self.__number_request_counter:
            return
        if not self._view or self._view.mode != ViewMode.CREATE:
            return
        self._view.set_order_number(number)

    async def __generate_order_number(self, order_date: date) -> str:
        sequence = await self.__get_next_order_sequence(order_date)
        return self.__format_order_number(order_date, sequence)

    async def __get_next_order_sequence(self, order_date: date) -> int:
        try:
            query_params = {"order_date": order_date.isoformat(), "page": 1, "page_size": 1}
            response = await self._service.get_page(Endpoint.SALES_ORDERS, None, query_params, None, self._module_id)
        except Exception:
            self._logger.exception("Failed to fetch sales order count for date.")
            return 1
        if not response:
            return 1
        return max(1, response.total + 1)

    @staticmethod
    def __format_order_number(order_date: date, sequence: int) -> str:
        date_part = order_date.strftime("%Y/%m/%d")
        suffix = "".join(random.choices(string.ascii_uppercase, k=3))
        return f"{date_part}/{suffix}/{sequence:04d}"

    @staticmethod
    def __get_latest_status_id(order_statuses: list[OrderViewStatusHistorySchema]) -> int | None:
        if not order_statuses:
            return None
        latest_status = max(order_statuses, key=lambda status: status.created_at)
        return latest_status.status_id
