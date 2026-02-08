from __future__ import annotations

from datetime import date, datetime
from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from schemas.business.trade.order_view_schema import (
    OrderViewDiscountSchema,
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewTargetItemSchema,
)
from schemas.core.param_schema import PaginatedResponseSchema
from services.business.trade import OrderService, OrderViewService
from utils.enums import ApiActionError, Endpoint, Module, View, ViewMode
from utils.media_url import MediaUrl
from utils.translation import Translation
from views.core.orders_view import OrdersView


class OrdersController(BaseViewController[OrderService, OrdersView, OrderPlainSchema, OrderStrictSchema]):
    _plain_schema_cls = OrderPlainSchema
    _strict_schema_cls = OrderStrictSchema
    _service_cls = OrderService
    _view_cls = OrdersView
    _endpoint = Endpoint.SALES_ORDERS
    _view_key = View.WEB_ORDERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_view_service = OrderViewService(self._settings, self._logger, self._tokens_accessor)
        self.__visible_order_ids: set[int] = set()

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> OrdersView:
        current_user = self._state_store.app_state.user.current
        customer_id = current_user.customer_id if current_user else None
        page_data = await self.__perform_get_sales_orders_page(customer_id)
        order_rows = page_data.items if page_data else []
        orders = [self.__to_order_summary(order) for order in order_rows]
        self.__visible_order_ids = {order["id"] for order in orders if isinstance(order.get("id"), int)}
        selected_order_id = self.__resolve_selected_order_id(orders)
        order_meta: dict[str, str] = {}
        order_items: list[dict[str, Any]] = []
        status_history: list[dict[str, str]] = []
        if selected_order_id is not None:
            view_data = await self.__perform_get_sales_view(selected_order_id)
            if view_data:
                discount_label_map = self.__build_discount_label_map(view_data)
                source_item_map = {row.id: row for row in view_data.source_items}
                images_map = self.__build_images_map(view_data.source_items)
                order_meta = self.__build_order_meta(view_data, discount_label_map)
                order_items = self.__build_order_items(
                    view_data.target_items,
                    source_item_map,
                    images_map,
                    discount_label_map,
                )
                status_history = self.__build_status_history(view_data.status_history, translation)
        return OrdersView(
            controller=self,
            translation=translation,
            orders=orders,
            selected_order_id=selected_order_id,
            order_meta=order_meta,
            order_items=order_items,
            status_history=status_history,
        )

    def on_new_order_clicked(self) -> None:
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=Module.WEB,
                view_key=View.WEB_CREATE_ORDER,
                mode=ViewMode.STATIC,
            ),
        )

    def on_order_selected(self, order_id: int) -> None:
        self._page.run_task(self.__handle_order_selected, order_id)

    async def __handle_order_selected(self, order_id: int) -> None:
        if not self._view:
            return
        if order_id not in self.__visible_order_ids:
            return
        self._view.set_selected_order(order_id)
        self._view.set_status_loading(True)
        view_data = await self.__perform_get_sales_view(order_id)
        if not view_data:
            self._view.set_status_loading(False)
            return
        translation = self._state_store.app_state.translation.items
        discount_label_map = self.__build_discount_label_map(view_data)
        source_item_map = {row.id: row for row in view_data.source_items}
        images_map = self.__build_images_map(view_data.source_items)
        order_meta = self.__build_order_meta(view_data, discount_label_map)
        order_items = self.__build_order_items(
            view_data.target_items,
            source_item_map,
            images_map,
            discount_label_map,
        )
        status_history = self.__build_status_history(view_data.status_history, translation)
        self._view.set_status_history(order_meta, order_items, status_history)
        self._view.set_status_loading(False)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_orders_page(self, customer_id: int | None) -> PaginatedResponseSchema[OrderPlainSchema] | None:
        if customer_id is None:
            return PaginatedResponseSchema[OrderPlainSchema](
                items=[],
                total=0,
                page=1,
                page_size=100,
                has_next=False,
                has_prev=False,
            )
        params: dict[str, str | int] = {
            "page": 1,
            "page_size": 100,
            "sort_by": "order_date",
            "order": "desc",
            "customer_id": customer_id,
        }
        return await self._service.get_page(Endpoint.SALES_ORDERS, None, params, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_view(self, order_id: int) -> OrderViewResponseSchema | None:
        return await self.__order_view_service.get_view(Endpoint.ORDER_VIEW_SALES, order_id, None, None, self._module_id)

    @staticmethod
    def __resolve_selected_order_id(orders: list[dict[str, Any]]) -> int | None:
        if not orders:
            return None
        first_id = orders[0].get("id")
        return int(first_id) if isinstance(first_id, int) else None

    def __to_order_summary(self, order: OrderPlainSchema) -> dict[str, Any]:
        return {
            "id": order.id,
            "number": order.number,
            "order_date": self.__format_date(order.order_date),
        }

    def __build_order_meta(self, view_data: OrderViewResponseSchema, discount_label_map: dict[int, str]) -> dict[str, str]:
        order = view_data.order
        if not order:
            return {}
        currency_map = {row.id: row.label for row in view_data.currencies}
        delivery_method_map = {row.id: row.label for row in view_data.delivery_methods}
        currency = currency_map.get(order.currency_id, "-")
        delivery_method = (
            delivery_method_map.get(order.delivery_method_id, "-") if order.delivery_method_id is not None else "-"
        )
        invoice_number = order.invoice_number.strip() if order.invoice_number else ""
        customer_discount = self.__resolve_customer_discount_label(view_data.target_items, discount_label_map)
        total_with_shipping = order.total_gross + order.shipping_cost
        meta = {
            "number": order.number,
            "order_date": self.__format_date(order.order_date),
            "currency": currency,
            "delivery_method": delivery_method,
            "customer_discount": customer_discount,
            "total_net": f"{order.total_net:.2f}",
            "total_vat": f"{order.total_vat:.2f}",
            "total_gross": f"{order.total_gross:.2f}",
            "total_discount": f"{order.total_discount:.2f}",
            "shipping_cost": f"{order.shipping_cost:.2f}",
            "total_with_shipping": f"{total_with_shipping:.2f}",
        }
        if invoice_number:
            meta["invoice_number"] = invoice_number
        return meta

    @staticmethod
    def __build_order_items(
        items: list[OrderViewTargetItemSchema],
        source_item_map: dict[int, OrderViewSourceItemSchema],
        images_map: dict[int, list[str]],
        discount_label_map: dict[int, str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for item in sorted(items, key=lambda row: (row.index, row.name, row.id)):
            source = source_item_map.get(item.item_id)
            discount_labels = OrdersController.__resolve_item_discount_labels(item, discount_label_map)
            width = source.width if source else item.width
            height = source.height if source else item.height
            length = source.length if source else item.length
            weight = source.weight if source else item.weight
            is_fragile = source.is_fragile if source else None
            expiration_date = source.expiration_date if source else None
            description = source.description if source else None
            category_name = source.category_name if source else None
            moq = source.moq if source else 1
            vat_rate = source.vat_rate if source else item.vat_rate
            ean = source.ean if source else "-"
            available = (
                max(0, source.stock_quantity - source.reserved_quantity)
                if source
                else None
            )
            rows.append(
                {
                    "item_id": item.item_id,
                    "index": item.index,
                    "name": item.name,
                    "ean": ean,
                    "quantity": str(item.quantity),
                    "discounts": ", ".join(discount_labels) if discount_labels else "-",
                    "description": description or "",
                    "is_fragile": is_fragile,
                    "expiration_date": str(expiration_date) if expiration_date else "",
                    "category_name": category_name or "",
                    "available": str(available) if available is not None else "",
                    "vat_rate": str(vat_rate),
                    "moq": str(moq),
                    "dimensions": f"{width}x{height}x{length}",
                    "weight": str(weight),
                    "images": images_map.get(item.item_id, []),
                }
            )
        return rows

    def __build_images_map(self, items: list[OrderViewSourceItemSchema]) -> dict[int, list[str]]:
        api_url = self._settings.API_URL
        if self._settings.PUBLIC_API_URL:
            api_url = self._settings.PUBLIC_API_URL
        result: dict[int, list[str]] = {}
        for item in items:
            urls: list[str] = []
            for image in item.images:
                if image.url:
                    resolved_url = MediaUrl.normalize(image.url, api_url)
                    urls.append(resolved_url or image.url)
            result[item.id] = urls
        return result

    @staticmethod
    def __build_discount_label_map(view_data: OrderViewResponseSchema) -> dict[int, str]:
        def absorb(discounts: list[OrderViewDiscountSchema], result: dict[int, str]) -> None:
            for discount in discounts:
                if discount.id not in result:
                    result[discount.id] = discount.code

        result: dict[int, str] = {}
        for customer in view_data.customers:
            absorb(customer.discounts, result)
        for category in view_data.categories:
            absorb(category.discounts, result)
        for item in view_data.source_items:
            absorb(item.discounts, result)
        return result

    @staticmethod
    def __resolve_item_discount_labels(item: OrderViewTargetItemSchema, discount_label_map: dict[int, str]) -> list[str]:
        labels: list[str] = []
        for discount_id in (item.item_discount_id, item.category_discount_id, item.customer_discount_id):
            if not isinstance(discount_id, int):
                continue
            label = discount_label_map.get(discount_id)
            if label and label not in labels:
                labels.append(label)
        return labels

    @staticmethod
    def __resolve_customer_discount_label(items: list[OrderViewTargetItemSchema], discount_label_map: dict[int, str]) -> str:
        labels: list[str] = []
        for item in items:
            discount_id = item.customer_discount_id
            if not isinstance(discount_id, int):
                continue
            label = discount_label_map.get(discount_id)
            if label and label not in labels:
                labels.append(label)
        if not labels:
            return "-"
        return ", ".join(labels)

    @staticmethod
    def __build_status_history(
        history: list[OrderViewStatusHistorySchema], translation: Translation
    ) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for row in sorted(history, key=lambda item: item.created_at):
            status_label = translation.get(row.key)
            created = OrdersController.__format_datetime(row.created_at)
            rows.append({"status": status_label, "created_at": created})
        return rows

    @staticmethod
    def __format_date(value: date) -> str:
        return value.strftime("%Y-%m-%d")

    @staticmethod
    def __format_datetime(value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")
