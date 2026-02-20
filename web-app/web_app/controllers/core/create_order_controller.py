from __future__ import annotations

import math
import random
import string
from datetime import date

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import CartUpdated, ViewRequested
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import (
    AssocOrderStatusPlainSchema,
    AssocOrderStatusStrictSchema,
)
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from schemas.business.trade.order_view_schema import (
    OrderViewDiscountSchema,
    OrderViewExchangeRateSchema,
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
)
from services.business.logistic import ItemService
from services.business.trade import (
    AssocOrderItemService,
    AssocOrderStatusService,
    OrderService,
    OrderViewService,
)
from utils.discount_context import DiscountContext
from utils.enums import ApiActionError, Endpoint, Module, View
from utils.media_url import MediaUrl
from utils.translation import Translation
from views.components.order_confirmation_dialog_component import OrderConfirmationDialogComponent
from views.core.create_order_view import CreateOrderView


class MissingExchangeRateError(RuntimeError):
    pass


class CreateOrderController(
    BaseViewController[ItemService, CreateOrderView, ItemPlainSchema, ItemStrictSchema],
):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = CreateOrderView
    _endpoint = Endpoint.ITEMS
    _view_key = View.WEB_CREATE_ORDER

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_view_service = OrderViewService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__cart: dict[int, dict[str, float | int | None]] = {}
        self.__item_pricing: dict[int, tuple[float, float, float]] = {}
        self.__item_dimensions: dict[int, tuple[float, float, float, float]] = {}
        self.__item_currency_map: dict[int, int | None] = {}
        self.__item_category_map: dict[int, int | None] = {}
        self.__item_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__category_discount_map: dict[int, list[OrderViewDiscountSchema]] = {}
        self.__customer_discounts: list[OrderViewDiscountSchema] = []
        self.__delivery_method_map: dict[int, tuple[float, float, float, float, float, int | None]] = {}
        self.__delivery_method_options: list[tuple[int, str]] = []
        self.__currency_label_map: dict[int, str] = {}
        self.__discount_percent_map: dict[int, float] = {}
        self.__exchange_rate_map: dict[tuple[int, int], float] = {}
        self.__exchange_rate_missing_notified = False
        self.__order_currency_id: int | None = None
        self.__checkout_missing_exchange_rate = False
        self.__default_status_id: int | None = None

    def compute_checkout_summary(
        self,
        currency_id: int | None,
        customer_discount_id: int | None,
        delivery_method_id: int | None,
    ) -> tuple[float, float, float, float, float, float, str, bool]:
        target_currency_id = currency_id or self.__order_currency_id
        if target_currency_id is None:
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "", False
        if not self.__cart:
            label = self.__currency_label_map.get(target_currency_id or 0, "")
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, label, False
        self.__checkout_missing_exchange_rate = False
        context = self.__build_cart_context(target_currency_id, track_missing=True)
        total_net = 0.0
        total_vat = 0.0
        total_gross = 0.0
        total_discount = 0.0
        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
            if quantity <= 0:
                continue
            net, vat, gross, discount = self.__calculate_cart_item_totals(
                item_id, quantity, context, customer_discount_id, target_currency_id, track_missing=True
            )
            total_net += net
            total_vat += vat
            total_gross += gross
            total_discount += discount
        shipping_cost = self.__compute_shipping_cost(delivery_method_id, target_currency_id, track_missing=True)
        total_with_shipping = total_gross + shipping_cost
        label = self.__currency_label_map.get(target_currency_id or 0, "")
        return (
            round(total_net, 2),
            round(total_vat, 2),
            round(total_gross, 2),
            round(total_discount, 2),
            round(shipping_cost, 2),
            round(total_with_shipping, 2),
            label,
            self.__checkout_missing_exchange_rate,
        )

    def get_cart_quantities(self) -> dict[int, int]:
        return {item_id: int(data.get("quantity") or 0) for item_id, data in self.__cart.items()}

    def get_cart_snapshot(self) -> list[dict[str, int | float | None]]:
        return [
            {
                "item_id": item_id,
                "quantity": int(data.get("quantity") or 0),
                "category_discount_id": data.get("category_discount_id"),
                "item_discount_id": data.get("item_discount_id"),
            }
            for item_id, data in self.__cart.items()
        ]

    def get_currency_options(self) -> list[tuple[int | str, str]]:
        return [(currency_id, label) for currency_id, label in self.__currency_label_map.items()]

    def get_customer_discount_options(self) -> list[tuple[int | str, str]]:
        return [
            (discount.id, f"{discount.code} ({(discount.percent or 0) * 100:.0f}%)")
            for discount in self.__customer_discounts
        ]

    def get_default_currency_id(self) -> int | None:
        return self.__order_currency_id

    def get_delivery_method_options(self) -> list[tuple[int | str, str]]:
        return list(self.__delivery_method_options)

    def on_add_to_cart(
        self,
        item_id: int,
        quantity: int,
        category_id: int | None,
        category_discount_id: int | None,
        item_discount_id: int | None,
    ) -> None:
        if quantity <= 0:
            return
        existing = self.__cart.get(item_id)
        total_quantity = quantity
        if existing:
            total_quantity += int(existing.get("quantity") or 0)
        self.__cart[item_id] = {
            "quantity": total_quantity,
            "category_id": category_id,
            "category_discount_id": category_discount_id,
            "item_discount_id": item_discount_id,
        }
        self.__recalculate_cart_prices()
        total = sum(self.__as_positive_int(value.get("quantity")) for value in self.__cart.values())
        self._page.run_task(self._event_bus.publish, CartUpdated(count=total))

    def on_back_to_orders_clicked(self) -> None:
        self._page.run_task(self.__open_orders_view)

    def on_category_discount_changed(self, category_id: int, selected_value: str) -> None:
        category_discount_id: int | None = None
        if selected_value and selected_value != "0":
            try:
                category_discount_id = int(selected_value)
            except ValueError:
                category_discount_id = None
        for item_id, item_data in self.__cart.items():
            if item_data.get("category_id") == category_id:
                item_data["category_discount_id"] = category_discount_id
        self.__recalculate_cart_prices()

    def on_checkout_confirm(
        self,
        currency_id: int | None,
        customer_discount_id: int | None,
        delivery_method_id: int | None,
    ) -> None:
        self._page.run_task(self.__handle_checkout_confirm, currency_id, customer_discount_id, delivery_method_id)

    def on_checkout_requested(self) -> None:
        if not self._view:
            return
        open_handler = getattr(self._view, "open_checkout_dialog", None)
        if callable(open_handler):
            open_handler()

    def on_item_discount_changed(self, item_id: int, selected_value: str | None) -> None:
        item_discount_id: int | None = None
        if selected_value and selected_value != "0":
            try:
                item_discount_id = int(selected_value)
            except ValueError:
                item_discount_id = None
        cart_item = self.__cart.get(item_id)
        if cart_item is None:
            return
        cart_item["item_discount_id"] = item_discount_id
        self.__recalculate_cart_prices()

    def remove_from_cart(self, item_id: int) -> None:
        if item_id not in self.__cart:
            return
        self.__cart.pop(item_id, None)
        self.__recalculate_cart_prices()
        total = sum(self.__as_positive_int(value.get("quantity")) for value in self.__cart.values())
        self._page.run_task(self._event_bus.publish, CartUpdated(count=total))

    async def _build_view(self, translation: Translation) -> CreateOrderView:
        view_data = await self.__perform_get_sales_view()
        self.__initialize_discount_maps(view_data)
        image_map, images_map = self.__build_image_maps(view_data.source_items)
        return CreateOrderView(
            controller=self,
            translation=translation,
            categories=view_data.categories,
            items=view_data.source_items,
            image_map=image_map,
            images_map=images_map,
        )

    def __build_cart_context(
        self,
        target_currency_id: int | None = None,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> DiscountContext:
        quantities: dict[int, int] = {}
        base_net_map: dict[int, float] = {}
        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
            if quantity <= 0:
                continue
            purchase_price, margin, _ = self.__item_pricing.get(item_id, (0.0, 0.0, 0.0))
            try:
                purchase_price = self.__convert_to_currency(
                    purchase_price,
                    self.__item_currency_map.get(item_id),
                    target_currency_id or self.__order_currency_id,
                    raise_on_missing=True,
                )
            except MissingExchangeRateError:
                if raise_on_missing:
                    raise
                if track_missing:
                    self.__checkout_missing_exchange_rate = True
            quantities[item_id] = quantity
            base_net_map[item_id] = self.__apply_margin(purchase_price, margin) * quantity

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

    def __build_image_maps(
        self, items: list[OrderViewSourceItemSchema]
    ) -> tuple[dict[int, str | None], dict[int, list[str]]]:
        api_url = self._settings.API_URL
        if self._settings.PUBLIC_API_URL:
            api_url = self._settings.PUBLIC_API_URL
        image_map: dict[int, str | None] = {}
        images_map: dict[int, list[str]] = {}
        for item in items:
            url = None
            urls: list[str] = []
            for image in item.images:
                if image.url:
                    resolved_url = MediaUrl.normalize(image.url, api_url)
                    urls.append(resolved_url or image.url)
                if image.is_primary:
                    url = MediaUrl.normalize(image.url, api_url)
            if url is None and item.images:
                url = MediaUrl.normalize(item.images[0].url, api_url)
            image_map[item.id] = url
            images_map[item.id] = urls
        return image_map, images_map

    def __calculate_cart_item_totals(
        self,
        item_id: int,
        quantity: int,
        context: DiscountContext,
        customer_discount_id: int | None = None,
        target_currency_id: int | None = None,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> tuple[float, float, float, float]:
        purchase_price, margin, vat_rate = self.__item_pricing.get(item_id, (0.0, 0.0, 0.0))
        try:
            purchase_price = self.__convert_to_currency(
                purchase_price,
                self.__item_currency_map.get(item_id),
                target_currency_id or self.__order_currency_id,
                raise_on_missing=True,
            )
        except MissingExchangeRateError:
            if raise_on_missing:
                raise
            if track_missing:
                self.__checkout_missing_exchange_rate = True
        base_net = self.__apply_margin(purchase_price, margin) * quantity
        discount_percent = self.__get_cart_discount_percent(
            item_id,
            quantity,
            base_net,
            context,
            customer_discount_id,
            target_currency_id,
            track_missing,
            raise_on_missing,
        )
        total_discount = round(base_net * discount_percent, 2) if discount_percent else 0.0
        total_net = round(base_net - total_discount, 2)
        total_vat = round(total_net * vat_rate, 2)
        total_gross = round(total_net + total_vat, 2)
        return total_net, total_vat, total_gross, total_discount

    def __compute_order_totals(
        self, currency_id: int, customer_discount_id: int | None, raise_on_missing: bool = False
    ) -> tuple[float, float, float, float]:
        context = self.__build_cart_context(currency_id, raise_on_missing=raise_on_missing)
        total_net = 0.0
        total_vat = 0.0
        total_gross = 0.0
        total_discount = 0.0
        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
            if quantity <= 0:
                continue
            net, vat, gross, discount = self.__calculate_cart_item_totals(
                item_id,
                quantity,
                context,
                customer_discount_id,
                currency_id,
                raise_on_missing=raise_on_missing,
            )
            total_net += net
            total_vat += vat
            total_gross += gross
            total_discount += discount
        return round(total_net, 2), round(total_vat, 2), round(total_gross, 2), round(total_discount, 2)

    def __compute_shipping_cost(
        self,
        delivery_method_id: int | None,
        target_currency_id: int,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> float:
        if not delivery_method_id:
            return 0.0
        delivery_method = self.__delivery_method_map.get(delivery_method_id)
        if not delivery_method:
            return 0.0
        price_per_unit, max_width, max_height, max_length, max_weight, carrier_currency_id = delivery_method
        total_width = 0.0
        total_height = 0.0
        total_length = 0.0
        total_weight = 0.0
        has_items = False

        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
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
        try:
            cost = self.__convert_to_currency(cost, carrier_currency_id, target_currency_id, raise_on_missing=True)
        except MissingExchangeRateError:
            if raise_on_missing:
                raise
            if track_missing:
                self.__checkout_missing_exchange_rate = True
        return round(cost, 2)

    def __convert_to_currency(
        self,
        amount: float,
        source_currency_id: int | None,
        target_currency_id: int | None,
        raise_on_missing: bool = False,
    ) -> float:
        if not target_currency_id or not source_currency_id:
            return amount
        if source_currency_id == target_currency_id:
            return amount
        rate = self.__exchange_rate_map.get((source_currency_id, target_currency_id))
        if rate is not None:
            return amount * rate
        reverse_rate = self.__exchange_rate_map.get((target_currency_id, source_currency_id))
        if reverse_rate:
            return amount / reverse_rate
        self.__notify_missing_exchange_rate()
        if raise_on_missing:
            raise MissingExchangeRateError(f"Missing exchange rate for {source_currency_id} -> {target_currency_id}.")
        return amount

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __create_order(self, payload: OrderStrictSchema) -> OrderPlainSchema:
        payload = payload.model_copy(update={"is_sales": True})
        return await self.__order_service.create(Endpoint.ORDERS, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __create_order_items(
        self, order_id: int, currency_id: int, customer_discount_id: int | None
    ) -> list[AssocOrderItemPlainSchema] | None:
        context = self.__build_cart_context(currency_id)
        payload: list[AssocOrderItemStrictSchema] = []
        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
            if quantity <= 0:
                continue
            purchase_price, margin, _ = self.__item_pricing.get(item_id, (0.0, 0.0, 0.0))
            purchase_price = self.__convert_to_currency(
                purchase_price, self.__item_currency_map.get(item_id), currency_id, raise_on_missing=True
            )
            base_net = self.__apply_margin(purchase_price, margin) * quantity
            (
                item_discount_id,
                category_discount_id,
                resolved_customer_discount_id,
            ) = self.__resolve_cart_discount_payload(
                item_id, quantity, base_net, context, customer_discount_id, currency_id
            )
            total_net, total_vat, total_gross, total_discount = self.__calculate_cart_item_totals(
                item_id,
                quantity,
                context,
                resolved_customer_discount_id,
                currency_id,
                raise_on_missing=True,
            )
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
                    category_discount_id=category_discount_id,
                    customer_discount_id=resolved_customer_discount_id,
                    item_discount_id=item_discount_id,
                    bin_id=None,
                )
            )
        if payload:
            return await self.__order_item_service.create_bulk(
                Endpoint.ORDER_ITEMS_CREATE_BULK, None, None, payload, self._module_id
            )
        return []

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __create_order_status(self, order_id: int) -> list[AssocOrderStatusPlainSchema] | None:
        status_id = self.__default_status_id
        if status_id is None:
            return []
        payload = AssocOrderStatusStrictSchema(order_id=order_id, status_id=status_id)
        return await self.__order_status_service.create_bulk(
            Endpoint.ORDER_STATUSES_CREATE_BULK, None, None, [payload], self._module_id
        )

    @staticmethod
    def __as_positive_int(value: float | int | None) -> int:
        if value is None:
            return 0
        parsed = int(value)
        if parsed <= 0:
            return 0
        return parsed

    @staticmethod
    def __apply_margin(purchase_price: float, margin: float) -> float:
        return purchase_price * (1 + margin)

    @staticmethod
    def __format_order_number(order_date: date, sequence: int) -> str:
        date_part = order_date.strftime("%Y/%m/%d")
        suffix = "".join(random.choices(string.ascii_uppercase, k=3))
        return f"{date_part}/{suffix}/{sequence:04d}"

    async def __generate_order_number(self, order_date: date) -> str:
        sequence = await self.__get_next_order_sequence(order_date)
        return self.__format_order_number(order_date, sequence)

    def __get_cart_discount_ids_for_item(
        self,
        item_id: int,
        quantity: int,
        base_net: float,
        context: DiscountContext,
        customer_discount_id: int | None = None,
        target_currency_id: int | None = None,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> list[int]:
        cart_data = self.__cart.get(item_id, {})
        discount_ids: list[int] = []

        item_discount_id = cart_data.get("item_discount_id")
        if isinstance(item_discount_id, int) and self.__is_discount_allowed(
            self.__item_discount_map.get(item_id, []),
            item_discount_id,
            quantity,
            base_net,
            target_currency_id,
            track_missing,
            raise_on_missing,
        ):
            discount_ids.append(item_discount_id)

        category_id = self.__item_category_map.get(item_id)
        category_discount_id = cart_data.get("category_discount_id")
        if (
            category_id is not None
            and isinstance(category_discount_id, int)
            and self.__is_discount_allowed(
                self.__category_discount_map.get(category_id, []),
                category_discount_id,
                context.category_quantities.get(category_id, 0),
                context.category_net_map.get(category_id, 0.0),
                target_currency_id,
                track_missing,
                raise_on_missing,
            )
        ):
            discount_ids.append(category_discount_id)

        if isinstance(customer_discount_id, int) and self.__is_discount_allowed(
            self.__customer_discounts,
            customer_discount_id,
            context.order_quantity,
            context.order_net,
            target_currency_id,
            track_missing,
            raise_on_missing,
        ):
            discount_ids.append(customer_discount_id)

        return discount_ids

    def __get_cart_discount_percent(
        self,
        item_id: int,
        quantity: int,
        base_net: float,
        context: DiscountContext,
        customer_discount_id: int | None = None,
        target_currency_id: int | None = None,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> float:
        discount_ids = self.__get_cart_discount_ids_for_item(
            item_id,
            quantity,
            base_net,
            context,
            customer_discount_id,
            target_currency_id,
            track_missing,
            raise_on_missing,
        )
        if not discount_ids:
            return 0.0
        return sum(self.__discount_percent_map.get(discount_id, 0.0) for discount_id in discount_ids)

    async def __get_next_order_sequence(self, order_date: date) -> int:
        try:
            query_params = {"order_date": order_date.isoformat(), "page": 1, "page_size": 1}
            response = await self.__order_service.get_page(
                Endpoint.SALES_ORDERS, None, query_params, None, self._module_id
            )
        except Exception:
            self._logger.exception("Failed to fetch sales order count for date.")
            return 1
        if not response:
            return 1
        return max(1, response.total + 1)

    async def __handle_checkout_confirm(
        self,
        currency_id: int | None,
        customer_discount_id: int | None,
        delivery_method_id: int | None,
    ) -> None:
        if not self.__cart:
            return
        if currency_id is None:
            return
        opened_loading = False
        created_order_number: str | None = None
        if self._loading_dialog is None:
            try:
                await self._open_loading_dialog()
                opened_loading = True
            except Exception:
                opened_loading = False
        try:
            user = self._state_store.app_state.user.current
            customer_id = user.customer_id if user else None
            totals = self.__compute_order_totals(currency_id, customer_discount_id, raise_on_missing=True)
            total_net, total_vat, total_gross, total_discount = totals
            try:
                shipping_cost = self.__compute_shipping_cost(
                    delivery_method_id, currency_id, track_missing=False, raise_on_missing=True
                )
            except MissingExchangeRateError:
                self._open_error_dialog(message_key="missing_exchange_rate")
                return
            order_date = date.today()
            order_number = await self.__generate_order_number(order_date)
            payload = OrderStrictSchema(
                number=order_number,
                is_sales=True,
                currency_id=currency_id,
                total_net=total_net,
                total_vat=total_vat,
                total_gross=total_gross,
                total_discount=total_discount,
                order_date=order_date,
                shipping_cost=shipping_cost,
                customer_id=customer_id,
                supplier_id=None,
                delivery_method_id=delivery_method_id,
                tracking_number=None,
                notes=None,
                external_notes=None,
                invoice_id=None,
            )
            order = await self.__create_order(payload)
            if not order:
                return
            items_created = await self.__create_order_items(order.id, currency_id, customer_discount_id)
            if items_created is None:
                return
            statuses_created = await self.__create_order_status(order.id)
            if statuses_created is None:
                return
            self.__cart.clear()
            self._page.run_task(self._event_bus.publish, CartUpdated(count=0))
            if self._view:
                self._view.refresh_items_list()
            created_order_number = order.number
        except MissingExchangeRateError:
            self._open_error_dialog(message_key="missing_exchange_rate")
            return
        finally:
            if opened_loading:
                self._close_loading_dialog()
        if created_order_number:
            await self.__open_orders_view()
            self.__show_order_confirmation(created_order_number)

    def __initialize_discount_maps(self, view_data: OrderViewResponseSchema) -> None:
        self.__item_pricing = {
            item.id: (item.purchase_price, item.margin, item.vat_rate) for item in view_data.source_items
        }
        self.__item_dimensions = {
            item.id: (item.width, item.height, item.length, item.weight) for item in view_data.source_items
        }
        self.__item_currency_map = {item.id: item.supplier_currency_id for item in view_data.source_items}
        self.__item_category_map = {item.id: item.category_id for item in view_data.source_items}
        self.__item_discount_map = {item.id: list(item.discounts) for item in view_data.source_items}
        self.__category_discount_map = {category.id: list(category.discounts) for category in view_data.categories}
        self.__currency_label_map = {currency.id: currency.label for currency in view_data.currencies}
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
        self.__delivery_method_options = [(item.id, item.label) for item in view_data.delivery_methods]
        default_status = next((item for item in view_data.statuses if item.status_number == 1), None)
        self.__default_status_id = default_status.id if default_status else None
        self.__customer_discounts = self.__get_current_customer_discounts(view_data)
        self.__discount_percent_map.clear()
        for discount_list in (
            self.__item_discount_map.values(),
            self.__category_discount_map.values(),
            [self.__customer_discounts],
        ):
            for discounts in discount_list:
                for discount in discounts:
                    if discount.percent is not None:
                        self.__discount_percent_map[discount.id] = discount.percent
        self.__order_currency_id = view_data.order.currency_id if view_data.order else None
        self.__load_exchange_rates(view_data.exchange_rates)

    def __get_current_customer_discounts(self, view_data: OrderViewResponseSchema) -> list[OrderViewDiscountSchema]:
        user = self._state_store.app_state.user.current
        customer_id = user.customer_id if user else None
        if customer_id is None:
            return []
        customer = next((item for item in view_data.customers if item.id == customer_id), None)
        if customer is None:
            return []
        return list(customer.discounts)

    def __is_discount_allowed(
        self,
        discounts: list[OrderViewDiscountSchema],
        discount_id: int,
        quantity: int,
        base_net: float,
        target_currency_id: int | None = None,
        track_missing: bool = False,
        raise_on_missing: bool = False,
    ) -> bool:
        discount = next((item for item in discounts if item.id == discount_id), None)
        if not discount:
            return False
        if discount.min_quantity is not None and quantity < discount.min_quantity:
            return False
        if discount.min_value is not None:
            if discount.currency_id is None:
                return False
            try:
                min_value = self.__convert_to_currency(
                    discount.min_value,
                    discount.currency_id,
                    target_currency_id or self.__order_currency_id,
                    raise_on_missing=True,
                )
            except MissingExchangeRateError:
                if raise_on_missing:
                    raise
                if track_missing:
                    self.__checkout_missing_exchange_rate = True
                return False
            if base_net < min_value:
                return False
        return True

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

    async def __open_orders_view(self) -> None:
        await self._event_bus.publish(
            ViewRequested(
                module_id=Module.WEB,
                view_key=View.WEB_ORDERS,
            )
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_view(self) -> OrderViewResponseSchema:
        return await self.__order_view_service.get_view(Endpoint.ORDER_VIEW_SALES, None, None, None, self._module_id)

    def __recalculate_cart_prices(self) -> None:
        if not self.__cart:
            return
        context = self.__build_cart_context()
        for item_id, data in self.__cart.items():
            quantity = int(data.get("quantity") or 0)
            if quantity <= 0:
                data["unit_net"] = 0.0
                data["unit_gross"] = 0.0
                data["total_net"] = 0.0
                data["total_gross"] = 0.0
                data["total_discount"] = 0.0
                continue
            total_net, _, total_gross, total_discount = self.__calculate_cart_item_totals(item_id, quantity, context)
            data["total_net"] = total_net
            data["total_gross"] = total_gross
            data["total_discount"] = total_discount
            unit_net = total_net / quantity if quantity else 0.0
            data["unit_net"] = unit_net
            data["unit_gross"] = (total_gross / quantity) if quantity else 0.0

    def __resolve_cart_discount_payload(
        self,
        item_id: int,
        quantity: int,
        base_net: float,
        context: DiscountContext,
        customer_discount_id: int | None,
        target_currency_id: int,
    ) -> tuple[int | None, int | None, int | None]:
        cart_data = self.__cart.get(item_id, {})
        item_discount_id = cart_data.get("item_discount_id")
        if not (
            isinstance(item_discount_id, int)
            and self.__is_discount_allowed(
                self.__item_discount_map.get(item_id, []),
                item_discount_id,
                quantity,
                base_net,
                target_currency_id,
            )
        ):
            item_discount_id = None
        category_discount_id = None
        category_id = self.__item_category_map.get(item_id)
        cart_category_discount_id = cart_data.get("category_discount_id")
        if (
            category_id is not None
            and isinstance(cart_category_discount_id, int)
            and self.__is_discount_allowed(
                self.__category_discount_map.get(category_id, []),
                cart_category_discount_id,
                context.category_quantities.get(category_id, 0),
                context.category_net_map.get(category_id, 0.0),
                target_currency_id,
            )
        ):
            category_discount_id = cart_category_discount_id
        resolved_customer_discount_id = None
        if isinstance(customer_discount_id, int) and self.__is_discount_allowed(
            self.__customer_discounts,
            customer_discount_id,
            context.order_quantity,
            context.order_net,
            target_currency_id,
        ):
            resolved_customer_discount_id = customer_discount_id
        return item_discount_id, category_discount_id, resolved_customer_discount_id

    def __show_order_confirmation(self, order_number: str) -> None:
        translation = self._state_store.app_state.translation.items
        dialog = OrderConfirmationDialogComponent(
            translation=translation,
            order_number=order_number,
            on_ok_clicked=lambda _: self._page.pop_dialog(),
        )
        self._queue_dialog(dialog)
