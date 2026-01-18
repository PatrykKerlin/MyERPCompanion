from datetime import date
import random
import string
import asyncio

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, PurchaseOrderStrictSchema
from services.base.base_service import BaseService
from services.business.logistic import DeliveryMethodService, ItemService
from services.business.trade import AssocOrderItemService, CurrencyService, OrderService, SupplierService
from schemas.core.param_schema import PaginatedResponseSchema
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from events.events import ViewRequested
from views.business.trade.purchase_order_view import PurchaseOrderView
from views.components.quantity_dialog_component import QuantityDialogComponent


class PurchaseOrderController(
    BaseViewController[OrderService, PurchaseOrderView, OrderPlainSchema, PurchaseOrderStrictSchema]
):
    _plain_schema_cls = OrderPlainSchema
    _strict_schema_cls = PurchaseOrderStrictSchema
    _service_cls = OrderService
    _view_cls = PurchaseOrderView
    _endpoint = Endpoint.ORDERS
    _view_key = View.PURCHASE_ORDERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__supplier_service = SupplierService(self._settings, self._logger, self._tokens_accessor)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__delivery_method_service = DeliveryMethodService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_items: dict[int, tuple[int, int]] = {}
        self.__pending_move_quantities: dict[int, int] = {}

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PurchaseOrderView:
        suppliers, currencies, delivery_methods = await asyncio.gather(
            self.__perform_get_all_suppliers(),
            self.__perform_get_all_currencies(),
            self.__perform_get_all_delivery_methods(),
        )
        self.__order_items = {}
        self.__pending_move_quantities.clear()
        source_items: list[tuple[int, str]] = []
        target_items: list[tuple[int, str]] = []
        if mode == ViewMode.READ and event.data:
            order_id = event.data["id"]
            supplier_id = event.data["supplier_id"]
            target_items = await self.__build_target_items(order_id)
            target_ids = {item_id for item_id, _ in target_items}
            source_items = await self.__perform_get_items_for_supplier(supplier_id, target_ids)
        return PurchaseOrderView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            None,
            suppliers,
            currencies,
            delivery_methods,
            source_items,
            target_items,
            self.on_order_items_save_clicked,
            self.on_order_items_move_requested,
            self.on_order_items_delete_clicked,
        )

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

    async def _perform_get_page(
        self, service: BaseService[OrderPlainSchema, PurchaseOrderStrictSchema], endpoint: Endpoint
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        return await super()._perform_get_page(service, Endpoint.PURCHASE_ORDERS)

    def get_create_defaults(self) -> dict[str, object]:
        return self.__build_create_defaults()

    def set_hidden_field_value(self, key: str, value: object) -> None:
        self._request_data.input_values[key] = value

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_suppliers(self) -> list[tuple[int, str]]:
        schemas = await self.__supplier_service.get_all(Endpoint.SUPPLIERS, None, None, None, self._module_id)
        return [(schema.id, schema.company_name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_delivery_methods(self) -> list[tuple[int, str]]:
        schemas = await self.__delivery_method_service.get_all(
            Endpoint.DELIVERY_METHODS, None, None, None, self._module_id
        )
        return [(schema.id, schema.name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_by_ids(self, item_ids: list[int]) -> list[tuple[int, str]]:
        if not item_ids:
            return []
        body_params = {"ids": item_ids}
        items = await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)
        return [(item.id, item.index) for item in items]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_for_supplier(self, supplier_id: int, exclude_ids: set[int]) -> list[tuple[int, str]]:
        query_params = {"supplier_id": supplier_id}
        items = await self.__item_service.get_all(Endpoint.ITEMS, None, query_params, None, self._module_id)
        results: list[tuple[int, str]] = []
        for item in items:
            if item.id in exclude_ids:
                continue
            results.append((item.id, item.index))
        return results

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_items(self, order_id: int) -> list[AssocOrderItemPlainSchema]:
        query_params = {"order_id": order_id}
        return await self.__order_item_service.get_all(Endpoint.ORDER_ITEMS, None, query_params, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.create_bulk(
            Endpoint.ORDER_ITEMS_CREATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_order_items(self, assoc_ids: list[int]) -> None:
        body_params = {"ids": assoc_ids}
        await self.__order_item_service.delete_bulk(
            Endpoint.ORDER_ITEMS_DELETE_BULK, None, None, body_params, self._module_id
        )

    async def __build_target_items(self, order_id: int) -> list[tuple[int, str]]:
        order_items = await self.__perform_get_order_items(order_id)
        self.__order_items = {item.item_id: (item.id, item.quantity) for item in order_items}
        item_ids = [item.item_id for item in order_items]
        if not item_ids:
            return []
        item_pairs = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item_id: label for item_id, label in item_pairs}
        targets: list[tuple[int, str]] = []
        for item in order_items:
            label = item_map.get(item.item_id, str(item.item_id))
            targets.append((item.item_id, f"{label} x{item.quantity}"))
        return targets

    async def __handle_move_with_quantity(self, item_id: int) -> None:
        if not self._view:
            return
        quantity = await self.__show_quantity_dialog()
        if not quantity:
            return
        self.__pending_move_quantities[item_id] = quantity
        self._view.move_source_items([item_id], highlight=True)

    async def __show_quantity_dialog(self) -> int | None:
        translation = self._state_store.app_state.translation.items
        dialog = QuantityDialogComponent(translation, 1000000)
        self._page.show_dialog(dialog)
        try:
            return await dialog.future
        finally:
            self._page.pop_dialog()

    async def __handle_order_items_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        supplier_id = self._view.data_row["supplier_id"]
        pending_ids = self._view.get_pending_item_ids()
        if not pending_ids:
            return
        payload: list[AssocOrderItemStrictSchema] = []
        for item_id in pending_ids:
            if item_id in self.__order_items:
                continue
            quantity = self.__pending_move_quantities.get(item_id, 1)
            payload.append(
                AssocOrderItemStrictSchema(
                    order_id=order_id,
                    item_id=item_id,
                    quantity=max(1, quantity),
                    total_net=0.01,
                    total_vat=0.01,
                    total_gross=0.01,
                    total_discount=0.01,
                    discount_id=None,
                )
            )
        if not payload:
            return
        await self.__perform_create_order_items(payload)
        await self.__refresh_order_item_lists(order_id, supplier_id)
        self.__pending_move_quantities.clear()

    async def __handle_order_items_delete(self, item_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        supplier_id = self._view.data_row["supplier_id"]
        assoc_ids = [self.__order_items[item_id][0] for item_id in item_ids if item_id in self.__order_items]
        if not assoc_ids:
            return
        await self.__perform_delete_order_items(assoc_ids)
        await self.__refresh_order_item_lists(order_id, supplier_id)

    async def __refresh_order_item_lists(self, order_id: int, supplier_id: int) -> None:
        if not self._view:
            return
        target_items = await self.__build_target_items(order_id)
        target_ids = {item_id for item_id, _ in target_items}
        source_items = await self.__perform_get_items_for_supplier(supplier_id, target_ids)
        self._view.set_target_items(target_items)
        self._view.set_source_items(source_items)

    def __build_create_defaults(self) -> dict[str, object]:
        today = date.today()
        date_part = today.strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        number = f"{date_part}{suffix}"
        tracking_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        shipping_cost = round(random.uniform(1, 1000), 2)
        return {
            "number": number,
            "is_sales": False,
            "total_net": 0.01,
            "total_vat": 0.01,
            "total_gross": 0.01,
            "total_discount": 0.01,
            "order_date": today,
            "tracking_number": tracking_number,
            "shipping_cost": shipping_cost,
            "notes": "",
            "internal_notes": "",
        }
