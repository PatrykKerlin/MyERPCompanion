import random
import string
from datetime import date
from typing import Any

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController, TServicePlainSchema, TServiceStrictSchema
from events.events import ViewRequested
from schemas.business.logistic.item_schema import ItemPlainSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema, PurchaseOrderStrictSchema
from schemas.business.trade.order_view_schema import (
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewTargetItemSchema,
)
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from services.base.base_service import BaseService
from services.business.logistic import ItemService
from services.business.trade import AssocOrderItemService, AssocOrderStatusService, OrderService, OrderViewService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
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
        self.__order_view_service = OrderViewService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__order_items: dict[int, tuple[int, int]] = {}
        self.__order_item_by_item_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__source_item_rows: dict[int, list[str]] = {}
        self.__item_pricing: dict[int, tuple[float, float]] = {}
        self.__supplier_currency_map: dict[int, int] = {}
        self.__default_status_id: int | None = None
        self.__current_status_id: int | None = None
        self.__default_currency_id: int | None = None

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
            "external_notes",
        }
        return [field for field in available_fields if field not in hidden_fields]

    def set_field_value(self, key: str, value: str | int | float | bool | date | None) -> None:
        if key == "is_sales":
            value = False
        super().set_field_value(key, value)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PurchaseOrderView:
        order_id = event.data.get("id") if event.data else None
        view_data = await self.__perform_get_purchase_view(order_id)
        suppliers = [(item.id, item.label) for item in view_data.suppliers]
        self.__supplier_currency_map = {item.id: item.currency_id for item in view_data.suppliers}
        currencies = [(item.id, item.label) for item in view_data.currencies]
        self.__default_currency_id = (
            min((item.id for item in view_data.currencies), default=None) if view_data.currencies else None
        )
        statuses = [(item.id, translation.get(item.label)) for item in view_data.statuses]
        status_steps = {item.id: item.status_number for item in view_data.statuses}
        self.__order_items = {}
        self.__order_item_by_item_id = {}
        self.__pending_move_quantities.clear()
        self.__source_item_rows.clear()
        self.__item_pricing.clear()
        self.__current_status_id = None
        default_status = next((item for item in view_data.statuses if item.status_number == 1), None)
        self.__default_status_id = default_status.id if default_status else None
        source_items = self.__build_source_item_rows(view_data.source_items)
        target_items = self.__build_target_item_rows(view_data.target_items)
        status_history = self.__build_status_history(view_data.status_history)
        order_data = event.data
        if view_data.order:
            order_data = view_data.order.model_dump()
            self._parse_data_row(order_data)
        self._request_data.input_values["delivery_method_id"] = None
        if mode in {ViewMode.READ, ViewMode.EDIT} and order_data:
            current_status_id = self.__get_latest_status_id(view_data.status_history)
            if current_status_id is None:
                current_status_id = self.__default_status_id
            if current_status_id is not None:
                order_data["status_id"] = current_status_id
                self.__current_status_id = current_status_id
            order_data["delivery_method_id"] = None
        bulk_transfer_enabled = False
        if mode == ViewMode.READ:
            bulk_transfer_enabled = self.__is_bulk_transfer_enabled(self.__current_status_id, status_steps)
        view = PurchaseOrderView(
            self,
            translation,
            mode,
            event.view_key,
            order_data,
            suppliers,
            currencies,
            statuses,
            source_items,
            target_items,
            status_history,
            bulk_transfer_enabled,
            self.__supplier_currency_map,
            self.on_order_items_save_clicked,
            self.on_order_items_move_requested,
            self.on_order_items_delete_clicked,
            self.on_order_items_pending_reverted,
        )
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
        return await super()._perform_get_page(service, Endpoint.PURCHASE_ORDERS)

    async def _perform_create(
        self,
        service: BaseService[OrderPlainSchema, PurchaseOrderStrictSchema],
        endpoint: Endpoint,
        payload: PurchaseOrderStrictSchema,
    ) -> OrderPlainSchema:
        payload = payload.model_copy(update={"is_sales": False})
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
        payload = payload.model_copy(update={"is_sales": False})
        response = await super()._perform_update(id, service, endpoint, payload)
        status_id = self._request_data.input_values.get("status_id")
        if status_id is not None and status_id != self.__current_status_id:
            await self.__perform_create_order_status(AssocOrderStatusStrictSchema(order_id=id, status_id=status_id))
            self.__current_status_id = status_id
        return response

    def __build_order_item_schema(
        self, order_id: int, item_id: int, quantity: int, assoc_id: int | None
    ) -> AssocOrderItemStrictSchema:
        total_net, total_vat, total_gross, total_discount = self.__calculate_item_totals(item_id, quantity)
        data = {
            "order_id": order_id,
            "item_id": item_id,
            "quantity": quantity,
            "to_process": quantity,
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_discount": total_discount,
            "bin_id": None,
            "category_discount_id": None,
            "customer_discount_id": None,
            "item_discount_id": None,
        }
        if assoc_id is not None:
            data["id"] = assoc_id
        return AssocOrderItemStrictSchema(**data)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_purchase_view(self, order_id: int | None) -> OrderViewResponseSchema:
        return await self.__order_view_service.get_view(
            Endpoint.ORDER_VIEW_PURCHASE, order_id, None, None, self._module_id
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
        valid_steps = [step for step in status_steps.values() if step is not None]
        if not valid_steps:
            return False
        current_step = status_steps.get(status_id)
        if current_step is None:
            return False
        return current_step == min(valid_steps)

    async def __ensure_item_pricing(self, item_ids: list[int]) -> None:
        missing_ids = [item_id for item_id in item_ids if item_id not in self.__item_pricing]
        if missing_ids:
            await self.__perform_get_items_by_ids(missing_ids)

    def __build_source_item_rows(self, items: list[OrderViewSourceItemSchema]) -> list[tuple[int, list[str]]]:
        results: list[tuple[int, list[str]]] = []
        for item in items:
            row = [item.index, item.name, item.ean]
            self.__source_item_rows[item.id] = row
            self.__item_pricing[item.id] = (item.purchase_price, item.vat_rate)
            results.append((item.id, row))
        return results

    def __build_target_item_rows(self, items: list[OrderViewTargetItemSchema]) -> list[tuple[int, list[str]]]:
        self.__order_items = {item.id: (item.item_id, item.quantity) for item in items}
        self.__order_item_by_item_id = {item.item_id: item.id for item in items}
        results: list[tuple[int, list[str]]] = []
        for item in items:
            row = [item.index, item.name, str(item.quantity)]
            self.__item_pricing[item.item_id] = (item.purchase_price, item.vat_rate)
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
        total_net = round(purchase_price * quantity, 2)
        total_vat = round(total_net * vat_rate, 2)
        total_gross = round(total_net + total_vat, 2)
        total_discount = 0.0
        return total_net, total_vat, total_gross, total_discount

    def __compute_order_totals(self, pending_targets: list[tuple[int, int]]) -> tuple[float, float, float, float]:
        pending_by_target = dict(pending_targets)
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
        dialog = QuantityDialogComponent(translation, 1000000, default_value=1, min_value=1)
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
                updates.append(self.__build_order_item_schema(order_id, item_id, total_quantity, target_id))
            else:
                payload.append(self.__build_order_item_schema(order_id, item_id, quantity, None))
        if not payload and not updates:
            return
        if payload:
            await self.__perform_create_order_items(payload)
        if updates:
            await self.__perform_update_order_items(updates)
        await self.__refresh_order_item_lists(order_id)
        self.__pending_move_quantities.clear()
        self.__recalculate_order_totals()

    async def __handle_order_items_delete(self, item_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        order_id = self._view.data_row["id"]
        assoc_ids = [item_id for item_id in item_ids if item_id in self.__order_items]
        if not assoc_ids:
            return
        await self.__perform_delete_order_items(assoc_ids)
        await self.__refresh_order_item_lists(order_id)

    async def __refresh_order_item_lists(self, order_id: int) -> None:
        if not self._view:
            return
        view_data = await self.__perform_get_purchase_view(order_id)
        target_items = self.__build_target_item_rows(view_data.target_items)
        source_items = self.__build_source_item_rows(view_data.source_items)
        self._view.set_target_rows(target_items)
        self._view.set_source_rows(source_items)
        self.__recalculate_order_totals()

    def __build_create_defaults(self) -> dict[str, Any]:
        today = date.today()
        date_part = today.strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
        number = f"{date_part}{suffix}"
        tracking_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
        shipping_cost = round(random.uniform(1, 1000), 2)
        defaults: dict[str, Any] = {
            "number": number,
            "is_sales": False,
            "currency_id": self.__default_currency_id,
            "delivery_method_id": None,
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

    @staticmethod
    def __get_latest_status_id(order_statuses: list[OrderViewStatusHistorySchema]) -> int | None:
        if not order_statuses:
            return None
        latest_status = max(order_statuses, key=lambda status: status.created_at)
        return latest_status.status_id
