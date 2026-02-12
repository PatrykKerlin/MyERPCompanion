import asyncio

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, ViewRequested
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
    OrderService,
    StatusService,
)
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.stock_receiving_view import StockReceivingView


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
        self.__order_items: dict[int, AssocOrderItemPlainSchema] = {}
        self.__order_item_quantities: dict[int, int] = {}
        self.__order_item_original_quantities: dict[int, int] = {}
        self.__order_item_labels: dict[int, tuple[str, str]] = {}
        self.__items_by_id: dict[int, ItemPlainSchema] = {}
        self.__target_items: dict[int, tuple[str, str, int, int]] = {}
        self.__target_bin_item_by_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__pending_move_item_ids: dict[int, int] = {}
        self.__target_rows: list[tuple[int, list[str]]] = []
        self.__current_order_id: int | None = None

    def on_order_changed(self, value: str | None) -> None:
        if not isinstance(self._view, StockReceivingView):
            return
        if not value or value == "0":
            self._view.set_order_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_order_error(None)
        order_id = int(value)
        self.__current_order_id = order_id
        self._page.run_task(self.__load_order_items, order_id)

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_target_bin_submit(self, location_value: str) -> None:
        if not isinstance(self._view, StockReceivingView):
            return
        location = location_value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self._page.run_task(self.__load_target_bin, location)

    def on_add_clicked(self, item_id: int | None, quantity: int | None) -> None:
        if item_id is None or quantity is None or quantity <= 0:
            self._open_error_dialog(message_key="value_required")
            return
        self._page.run_task(self.__handle_add_with_quantity, item_id, quantity)

    def on_pending_item_removed(self, target_id: int) -> None:
        quantity = self.__pending_move_quantities.pop(target_id, 0)
        item_id = self.__pending_move_item_ids.pop(target_id, None)
        if item_id is not None and quantity:
            self.__order_item_quantities[item_id] = self.__order_item_quantities.get(item_id, 0) + quantity
        self.__refresh_source_rows()

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__handle_save)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> StockReceivingView:
        self.__target_bin = None
        self.__order_items = {}
        self.__order_item_quantities = {}
        self.__order_item_original_quantities = {}
        self.__order_item_labels = {}
        self.__items_by_id = {}
        self.__target_items = {}
        self.__target_bin_item_by_id = {}
        self.__pending_move_quantities = {}
        self.__pending_move_item_ids = {}
        self.__target_rows = []
        self.__current_order_id = None

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

    async def __handle_save(self) -> None:
        await self.__handle_bulk_transfer_save()
        if isinstance(self._view, StockReceivingView):
            self._view.clear_pending_rows()

    async def __handle_add_with_quantity(self, item_id: int, quantity: int) -> None:
        if not isinstance(self._view, StockReceivingView):
            return
        max_quantity = self.__order_item_quantities.get(item_id, 0)
        if max_quantity <= 0:
            return
        bounded_quantity = min(quantity, max_quantity)
        if bounded_quantity <= 0:
            return

        await self.__ensure_item_label(item_id)
        target_item = self.__target_items.get(item_id)
        if target_item:
            item_index, item_name, bin_item_id, current_quantity = target_item
            current_pending = self.__pending_move_quantities.get(bin_item_id, 0)
            self._view.update_existing_target(
                bin_item_id,
                item_id,
                [item_index, item_name, str(current_quantity + current_pending + bounded_quantity)],
            )
            self.__pending_move_quantities[bin_item_id] = current_pending + bounded_quantity
            self.__pending_move_item_ids[bin_item_id] = item_id
        else:
            item_index, item_name = self.__order_item_labels.get(item_id, (str(item_id), ""))
            target_id = self._view.add_target_row(item_id, [item_index, item_name, str(bounded_quantity)])
            self.__pending_move_quantities[target_id] = self.__pending_move_quantities.get(target_id, 0) + bounded_quantity
            self.__pending_move_item_ids[target_id] = item_id

        self.__order_item_quantities[item_id] = max(0, max_quantity - bounded_quantity)
        self.__refresh_source_rows()

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_purchase_orders_by_status_id(self, status_id: int) -> list[OrderPlainSchema]:
        return await self.__order_service.get_all(
            Endpoint.PURCHASE_ORDERS,
            None,
            {"status_id": status_id},
            None,
            self._module_id,
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

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_order_items(self, items: list[AssocOrderItemStrictSchema]) -> None:
        await self.__order_item_service.update_bulk(
            Endpoint.ORDER_ITEMS_UPDATE_BULK, None, None, items, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_item(self, item_id: int, payload: ItemStrictSchema) -> None:
        await self.__item_service.update(Endpoint.ITEMS, item_id, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_order_status(self, payload: AssocOrderStatusStrictSchema) -> None:
        await self.__order_status_service.create(Endpoint.ORDER_STATUSES, None, None, payload, self._module_id)

    async def __load_mobile_eligible_orders(self) -> list[OrderPlainSchema]:
        statuses = await self.__perform_get_all_statuses()
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

    async def __load_order_items(self, order_id: int) -> None:
        if not self._view:
            return
        self.__pending_move_quantities.clear()
        self.__pending_move_item_ids.clear()
        order_items = await self.__perform_get_order_items(order_id)
        if not order_items:
            self.__order_items = {}
            self.__order_item_quantities = {}
            self.__order_item_original_quantities = {}
            self.__order_item_labels = {}
            self.__items_by_id = {}
            self._view.set_source_rows([])
            self._view.set_source_enabled(False)
            return
        self.__order_items = {item.item_id: item for item in order_items}
        self.__order_item_quantities = {item.item_id: max(0, item.to_process) for item in order_items}
        self.__order_item_original_quantities = {item.item_id: max(0, item.to_process) for item in order_items}
        item_ids = [item.item_id for item in order_items]
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        self.__items_by_id = item_map
        self.__order_item_labels = {}
        source_rows: list[tuple[int, list[str]]] = []
        for item in order_items:
            if item.to_process <= 0:
                continue
            item_schema = item_map.get(item.item_id)
            if item_schema:
                self.__order_item_labels[item.item_id] = (item_schema.index, item_schema.name)
                source_rows.append((item.item_id, [item_schema.index, item_schema.name, str(item.to_process)]))
            else:
                self.__order_item_labels[item.item_id] = (str(item.item_id), "")
                source_rows.append((item.item_id, [str(item.item_id), "", str(item.to_process)]))
        self._view.set_source_rows(source_rows)
        self._view.set_source_enabled(bool(source_rows))
        if self.__target_rows:
            self._view.set_target_rows(self.__target_rows)
        self.__sync_transfer_state()

    async def __load_target_bin(self, location: str) -> None:
        if not self._view:
            return
        target_bin = await self.__perform_get_single_bin(location)
        selected_warehouse_id = self._get_mobile_selected_warehouse_id()
        if (
            selected_warehouse_id is not None
            and target_bin is not None
            and target_bin.warehouse_id != selected_warehouse_id
        ):
            target_bin = None
        if not target_bin:
            self.__target_bin = None
            self.__target_items = {}
            self.__target_bin_item_by_id = {}
            self.__target_rows = []
            self._view.set_target_error(self._state_store.app_state.translation.items.get("bin_not_found"))
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            self.__sync_transfer_state()
            return
        if not target_bin.is_inbound:
            self.__target_bin = None
            self.__target_items = {}
            self.__target_bin_item_by_id = {}
            self.__target_rows = []
            self._view.set_target_error(self._state_store.app_state.translation.items.get("bin_not_inbound"))
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            self.__sync_transfer_state()
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
        self.__sync_transfer_state()

    def __sync_transfer_state(self) -> None:
        if not self._view:
            return
        has_target_bin = self.__target_bin is not None
        has_order = self.__current_order_id is not None
        source_available = any(remaining > 0 for remaining in self.__order_item_quantities.values()) or bool(
            self.__pending_move_item_ids
        )
        source_enabled = has_target_bin and has_order and source_available
        target_enabled = has_target_bin and has_order
        self._view.set_source_enabled(source_enabled)
        self._view.set_target_enabled(target_enabled)

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view or not self.__target_bin:
            return
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        creates: list[AssocBinItemStrictSchema] = []
        updates: list[AssocBinItemStrictSchema] = []
        order_item_updates: list[AssocOrderItemStrictSchema] = []
        touched_item_ids: set[int] = set()
        moved_by_item: dict[int, int] = {}
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
            touched_item_ids.add(item_id)
            moved_by_item[item_id] = moved_by_item.get(item_id, 0) + move_quantity
        for item_id in touched_item_ids:
            order_item = self.__order_items.get(item_id)
            if not order_item:
                continue
            new_to_process = max(0, self.__order_item_quantities.get(item_id, 0))
            order_item_updates.append(
                AssocOrderItemStrictSchema(
                    id=order_item.id,
                    order_id=order_item.order_id,
                    item_id=order_item.item_id,
                    quantity=order_item.quantity,
                    total_net=order_item.total_net,
                    total_vat=order_item.total_vat,
                    total_gross=order_item.total_gross,
                    total_discount=order_item.total_discount,
                    to_process=new_to_process,
                    bin_id=order_item.bin_id,
                    category_discount_id=order_item.category_discount_id,
                    customer_discount_id=order_item.customer_discount_id,
                    item_discount_id=order_item.item_discount_id,
                )
            )
        if creates:
            await self.__perform_create_bin_items(creates)
        if updates:
            await self.__perform_update_bin_items(updates)
        if order_item_updates:
            await self.__perform_update_order_items(order_item_updates)
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
                new_stock = item_schema.stock_quantity + moved_quantity
                update_tasks.append(
                    self.__perform_update_item(item_id, self.__build_item_update(item_schema, new_stock))
                )
            if update_tasks:
                await asyncio.gather(*update_tasks)
        await self.__load_target_bin(self.__target_bin.location)
        self.__pending_move_quantities.clear()
        self.__pending_move_item_ids.clear()
        if self.__current_order_id is not None:
            await self.__load_order_items(self.__current_order_id)
            await self.__check_and_update_order_status(self.__current_order_id)

    def __refresh_source_rows(self) -> None:
        if not self._view:
            return
        source_rows: list[tuple[int, list[str]]] = []
        pending_item_ids = set(self.__pending_move_item_ids.values())
        for item_id, remaining in self.__order_item_quantities.items():
            if remaining <= 0 and item_id not in pending_item_ids:
                continue
            if item_id in pending_item_ids:
                display_quantity = self.__order_item_original_quantities.get(item_id, remaining)
            else:
                display_quantity = remaining
            label = self.__order_item_labels.get(item_id)
            if label:
                source_rows.append((item_id, [label[0], label[1], str(display_quantity)]))
            else:
                source_rows.append((item_id, [str(item_id), "", str(display_quantity)]))
        self._view.set_source_rows(source_rows)
        if pending_item_ids:
            self._view.mark_source_items_as_moved(list(pending_item_ids))
        self._view.set_source_enabled(bool(source_rows))
        self.__sync_transfer_state()

    async def __check_and_update_order_status(self, order_id: int) -> None:
        order_items = await self.__perform_get_order_items(order_id)
        if not order_items:
            return
        if any(item.to_process > 0 for item in order_items):
            return
        statuses = await self.__perform_get_all_statuses()
        target_status = next((status for status in statuses if status.order == 8), None)
        if not target_status:
            return
        order_statuses = await self.__perform_get_order_statuses(order_id)
        if order_statuses:
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            if latest_status.status_id == target_status.id:
                return
        await self.__perform_create_order_status(
            AssocOrderStatusStrictSchema(order_id=order_id, status_id=target_status.id)
        )

    async def __ensure_item_label(self, item_id: int) -> None:
        label = self.__order_item_labels.get(item_id)
        if label and label[1]:
            return
        item_schema = self.__items_by_id.get(item_id)
        if not item_schema:
            items = await self.__perform_get_items_by_ids([item_id])
            item_schema = items[0] if items else None
            if item_schema:
                self.__items_by_id[item_schema.id] = item_schema
        if item_schema:
            self.__order_item_labels[item_id] = (item_schema.index, item_schema.name)

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
