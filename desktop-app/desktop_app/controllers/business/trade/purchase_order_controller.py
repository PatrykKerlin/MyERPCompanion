from datetime import date
from typing import Any
import random
import string
import asyncio

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import (
    AssocOrderStatusPlainSchema,
    AssocOrderStatusStrictSchema,
)
from schemas.business.trade.order_schema import OrderPlainSchema, PurchaseOrderStrictSchema
from services.base.base_service import BaseService
from services.business.logistic import DeliveryMethodService, ItemService
from schemas.business.logistic.item_schema import ItemPlainSchema
from services.business.trade import (
    AssocOrderItemService,
    AssocOrderStatusService,
    CurrencyService,
    OrderService,
    StatusService,
    SupplierService,
)
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
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
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__order_items: dict[int, tuple[int, int]] = {}
        self.__order_item_by_item_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__source_item_rows: dict[int, list[str]] = {}
        self.__item_pricing: dict[int, tuple[float, float]] = {}
        self.__default_status_id: int | None = None
        self.__current_status_id: int | None = None

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PurchaseOrderView:
        suppliers, currencies, delivery_methods, statuses = await asyncio.gather(
            self.__perform_get_all_suppliers(),
            self.__perform_get_all_currencies(),
            self.__perform_get_all_delivery_methods(),
            self.__perform_get_all_statuses(),
        )
        self.__order_items = {}
        self.__order_item_by_item_id = {}
        self.__pending_move_quantities.clear()
        self.__source_item_rows.clear()
        self.__item_pricing.clear()
        self.__current_status_id = None
        source_items: list[tuple[int, list[str]]] = []
        target_items: list[tuple[int, list[str]]] = []
        status_history: list[dict[str, Any]] = []
        order_id = 0
        supplier_id = 0
        if mode in {ViewMode.READ, ViewMode.EDIT} and event.data:
            order_id = event.data["id"]
            supplier_id = event.data["supplier_id"]
            order_statuses = await self.__perform_get_order_statuses(order_id)
            status_name_by_id = {status_id: name for status_id, name in statuses}
            status_history = self.__build_status_history(order_statuses, status_name_by_id)
            current_status_id = self.__get_oldest_status_id(order_statuses)
            if current_status_id is None:
                current_status_id = self.__default_status_id
            if current_status_id is not None:
                event.data["status_id"] = current_status_id
                self.__current_status_id = current_status_id
        view = PurchaseOrderView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            suppliers,
            currencies,
            statuses,
            delivery_methods,
            source_items,
            target_items,
            status_history,
            self.on_order_items_save_clicked,
            self.on_order_items_move_requested,
            self.on_order_items_delete_clicked,
            self.on_order_items_pending_reverted,
        )
        if mode in {ViewMode.READ, ViewMode.EDIT}:
            totals = self.__compute_order_totals([])
            view.set_order_totals(*totals)
            if event.data:
                self._page.run_task(self.__load_order_item_lists, order_id, supplier_id)
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
        self, service: BaseService[OrderPlainSchema, PurchaseOrderStrictSchema], endpoint: Endpoint
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        return await super()._perform_get_page(service, Endpoint.PURCHASE_ORDERS)

    def get_create_defaults(self) -> dict[str, object]:
        return self.__build_create_defaults()

    def set_hidden_field_value(self, key: str, value: object) -> None:
        self._request_data.input_values[key] = value

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        if key == "is_sales":
            value = False
        super().set_field_value(key, value)

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
    async def __perform_get_all_statuses(self) -> list[tuple[int, str]]:
        schemas = await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)
        sorted_schemas = sorted(schemas, key=lambda status: status.step_number)
        if sorted_schemas:
            self.__default_status_id = sorted_schemas[0].id
        return [(schema.id, schema.name) for schema in sorted_schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_by_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        if not item_ids:
            return []
        body_params = IdsPayloadSchema(ids=item_ids)
        items = await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)
        for item in items:
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
        return items

    async def __ensure_item_pricing(self, item_ids: list[int]) -> None:
        missing_ids = [item_id for item_id in item_ids if item_id not in self.__item_pricing]
        if missing_ids:
            await self.__perform_get_items_by_ids(missing_ids)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_for_supplier(
        self, supplier_id: int, exclude_ids: set[int]
    ) -> list[tuple[int, list[str]]]:
        query_params = {"supplier_id": supplier_id}
        items = await self.__item_service.get_all(Endpoint.ITEMS, None, query_params, None, self._module_id)
        results: list[tuple[int, list[str]]] = []
        for item in items:
            if item.id in exclude_ids:
                continue
            row = [item.index, item.name, item.ean]
            self.__source_item_rows[item.id] = row
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
            results.append((item.id, row))
        return results

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_items(self, order_id: int) -> list[AssocOrderItemPlainSchema]:
        query_params = {"order_id": order_id}
        return await self.__order_item_service.get_all(Endpoint.ORDER_ITEMS, None, query_params, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_order_statuses(self, order_id: int) -> list[AssocOrderStatusPlainSchema]:
        query_params = {"order_id": order_id}
        return await self.__order_status_service.get_all(
            Endpoint.ORDER_STATUSES, None, query_params, None, self._module_id
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

    @staticmethod
    def __get_oldest_status_id(order_statuses: list[AssocOrderStatusPlainSchema]) -> int | None:
        if not order_statuses:
            return None
        oldest_status = min(order_statuses, key=lambda status: status.created_at)
        return oldest_status.status_id

    def __build_status_history(
        self,
        order_statuses: list[AssocOrderStatusPlainSchema],
        status_name_by_id: dict[int, str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for status in sorted(order_statuses, key=lambda item: item.created_at):
            rows.append(
                {
                    "status": status_name_by_id.get(status.status_id, str(status.status_id)),
                    "created_at": self._format_datetime(status.created_at),
                }
            )
        return rows

    async def __build_target_items(self, order_id: int) -> list[tuple[int, list[str]]]:
        order_items = await self.__perform_get_order_items(order_id)
        self.__order_items = {item.id: (item.item_id, item.quantity) for item in order_items}
        self.__order_item_by_item_id = {item.item_id: item.id for item in order_items}
        item_ids = [item.item_id for item in order_items]
        if not item_ids:
            return []
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        targets: list[tuple[int, list[str]]] = []
        for item in order_items:
            item_schema = item_map.get(item.item_id)
            if item_schema:
                row = [item_schema.index, item_schema.name, str(item.quantity)]
            else:
                row = [str(item.item_id), "", str(item.quantity)]
            targets.append((item.id, row))
        return targets

    def __calculate_item_totals(self, item_id: int, quantity: int) -> tuple[float, float, float, float]:
        purchase_price, vat_rate = self.__item_pricing.get(item_id, (0.0, 0.0))
        total_net = round(purchase_price * quantity, 2)
        total_vat = round(total_net * vat_rate, 2)
        total_gross = round(total_net + total_vat, 2)
        total_discount = 0.0
        return total_net, total_vat, total_gross, total_discount

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
        totals = self.__compute_order_totals(self._view.get_pending_targets())
        self._view.set_order_totals(*totals)

    async def __handle_move_with_quantity(self, item_id: int) -> None:
        if not self._view:
            return
        await self.__ensure_item_pricing([item_id])
        quantity = await self.__show_quantity_dialog()
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

    async def __show_quantity_dialog(self) -> int | None:
        translation = self._state_store.app_state.translation.items
        dialog = QuantityDialogComponent(translation, 1000000, default_value=0, min_value=0)
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
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        await self.__ensure_item_pricing([item_id for _, item_id in pending_targets])
        payload: list[AssocOrderItemStrictSchema] = []
        updates: list[AssocOrderItemStrictSchema] = []
        for target_id, item_id in pending_targets:
            quantity = self.__pending_move_quantities.get(target_id, 1)
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
                        quantity=max(1, total_quantity),
                        total_net=total_net,
                        total_vat=total_vat,
                        total_gross=total_gross,
                        total_discount=total_discount,
                        discount_id=None,
                    )
                )
            else:
                total_net, total_vat, total_gross, total_discount = self.__calculate_item_totals(item_id, quantity)
                payload.append(
                    AssocOrderItemStrictSchema(
                        order_id=order_id,
                        item_id=item_id,
                        quantity=max(1, quantity),
                        total_net=total_net,
                        total_vat=total_vat,
                        total_gross=total_gross,
                        total_discount=total_discount,
                        discount_id=None,
                    )
                )
        if not payload and not updates:
            return
        if payload:
            await self.__perform_create_order_items(payload)
        if updates:
            await self.__perform_update_order_items(updates)
        await self.__refresh_order_item_lists(order_id, supplier_id)
        self.__pending_move_quantities.clear()
        self.__recalculate_order_totals()

    async def __handle_order_items_delete(self, item_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        supplier_id = self._view.data_row["supplier_id"]
        assoc_ids = [item_id for item_id in item_ids if item_id in self.__order_items]
        if not assoc_ids:
            return
        await self.__perform_delete_order_items(assoc_ids)
        await self.__refresh_order_item_lists(order_id, supplier_id)

    async def __refresh_order_item_lists(self, order_id: int, supplier_id: int) -> None:
        if not self._view:
            return
        target_items = await self.__build_target_items(order_id)
        source_items = await self.__perform_get_items_for_supplier(supplier_id, set())
        self._view.set_target_rows(target_items)
        self._view.set_source_rows(source_items)
        self.__recalculate_order_totals()

    async def __load_order_item_lists(self, order_id: int, supplier_id: int) -> None:
        await self.__refresh_order_item_lists(order_id, supplier_id)

    def __build_create_defaults(self) -> dict[str, object]:
        today = date.today()
        date_part = today.strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        number = f"{date_part}{suffix}"
        tracking_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        shipping_cost = round(random.uniform(1, 1000), 2)
        defaults: dict[str, object] = {
            "number": number,
            "is_sales": False,
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
        service: BaseService[OrderPlainSchema, PurchaseOrderStrictSchema],
        endpoint: Endpoint,
        payload: PurchaseOrderStrictSchema,
    ) -> OrderPlainSchema:
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
        service: BaseService[OrderPlainSchema, PurchaseOrderStrictSchema],
        endpoint: Endpoint,
        payload: PurchaseOrderStrictSchema,
    ) -> OrderPlainSchema:
        response = await super()._perform_update(id, service, endpoint, payload)
        status_id = self._request_data.input_values.get("status_id")
        if status_id is not None and status_id != self.__current_status_id:
            await self.__perform_create_order_status(AssocOrderStatusStrictSchema(order_id=id, status_id=status_id))
            self.__current_status_id = status_id
        return response
