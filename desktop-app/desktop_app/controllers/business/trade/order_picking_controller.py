import asyncio
import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.business.trade.assoc_order_item_schema import AssocOrderItemPlainSchema, AssocOrderItemStrictSchema
from schemas.business.trade.assoc_order_status_schema import AssocOrderStatusPlainSchema, AssocOrderStatusStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema
from schemas.business.trade.status_schema import StatusPlainSchema
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from services.business.trade import AssocOrderItemService, AssocOrderStatusService, OrderService, StatusService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.order_picking_view import OrderPickingView
from views.components.quantity_dialog_component import QuantityDialogComponent


class OrderPickingController(
    BaseViewController[AssocBinItemService, OrderPickingView, AssocBinItemPlainSchema, AssocBinItemStrictSchema]
):
    _plain_schema_cls = AssocBinItemPlainSchema
    _strict_schema_cls = AssocBinItemStrictSchema
    _service_cls = AssocBinItemService
    _view_cls = OrderPickingView
    _endpoint = Endpoint.BIN_ITEMS
    _view_key = View.ORDER_PICKING

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__bin_item_service = self._service
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__order_item_service = AssocOrderItemService(self._settings, self._logger, self._tokens_accessor)
        self.__order_status_service = AssocOrderStatusService(self._settings, self._logger, self._tokens_accessor)
        self.__status_service = StatusService(self._settings, self._logger, self._tokens_accessor)

        self.__source_bin: BinPlainSchema | None = None
        self.__order_items: dict[int, AssocOrderItemPlainSchema] = {}
        self.__order_item_quantities: dict[int, int] = {}
        self.__order_item_original_quantities: dict[int, int] = {}
        self.__order_item_labels: dict[int, tuple[str, str]] = {}
        self.__items_by_id: dict[int, ItemPlainSchema] = {}
        self.__source_items: dict[int, tuple[str, str, int, int]] = {}
        self.__source_bin_item_by_id: dict[int, int] = {}
        self.__pending_move_quantities: dict[int, int] = {}
        self.__pending_move_item_ids: dict[int, int] = {}
        self.__source_rows: list[tuple[int, list[object]]] = []
        self.__current_order_id: int | None = None

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> OrderPickingView:
        mode = ViewMode.STATIC
        orders = await self.__load_eligible_orders()
        order_pairs = [(order.id, order.number) for order in orders]
        return OrderPickingView(
            self,
            translation,
            mode,
            event.view_key,
            order_pairs,
            self.on_source_bin_submit,
            self.on_bulk_transfer_save_clicked,
            self.on_bulk_transfer_move_requested,
            self.on_bulk_transfer_pending_reverted,
        )

    def on_order_changed(self, value: str | None) -> None:
        if not self._view:
            return
        if not value or value == "0":
            self._view.set_order_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_order_error(None)
        order_id = int(value)
        self.__current_order_id = order_id
        self._page.run_task(self.__load_order_items, order_id)

    def on_source_bin_submit(self, event: ft.Event[ft.TextField]) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_source_bin_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_source_bin_error(None)
        self._page.run_task(self.__load_source_bin, location)

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
        source_item = self.__source_items.get(item_id)
        if not source_item:
            return
        bin_item_id = source_item[2]
        bin_quantity = source_item[3]
        pending_quantity = self.__pending_move_quantities.get(bin_item_id, 0)
        available_bin = max(0, bin_quantity - pending_quantity)
        max_quantity = min(max_quantity, available_bin)
        if max_quantity <= 0:
            return
        self._page.run_task(self.__handle_move_with_quantity, item_id, max_quantity)

    def on_bulk_transfer_pending_reverted(self, target_ids: list[int]) -> None:
        for target_id in target_ids:
            quantity = self.__pending_move_quantities.pop(target_id, 0)
            item_id = self.__pending_move_item_ids.pop(target_id, None)
            if item_id is not None and quantity:
                self.__order_item_quantities[item_id] = self.__order_item_quantities.get(item_id, 0) + quantity
        self.__refresh_source_rows()

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_statuses(self) -> list[StatusPlainSchema]:
        return await self.__status_service.get_all(Endpoint.STATUSES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_orders(self) -> PaginatedResponseSchema[OrderPlainSchema]:
        return await self.__order_service.get_page(
            Endpoint.SALES_ORDERS, None, {"page": 1, "page_size": 200}, None, self._module_id
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
    async def __perform_update_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.update_bulk(Endpoint.BIN_ITEMS_UPDATE_BULK, None, None, items, self._module_id)

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_bin_items(self, ids: list[int]) -> None:
        body_params = IdsPayloadSchema(ids=ids)
        await self.__bin_item_service.delete_bulk(
            Endpoint.BIN_ITEMS_DELETE_BULK, None, None, body_params, self._module_id
        )

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

    async def __load_eligible_orders(self) -> list[OrderPlainSchema]:
        statuses = await self.__perform_get_all_statuses()
        status_by_id = {status.id: status for status in statuses}
        response = await self.__perform_get_sales_orders()
        orders = response.items
        eligible: list[OrderPlainSchema] = []
        for order in orders:
            order_statuses = await self.__perform_get_order_statuses(order.id)
            if not order_statuses:
                continue
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            status = status_by_id.get(latest_status.status_id)
            if status and status.order in {2, 3}:
                eligible.append(order)
        return eligible

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
        source_rows: list[tuple[int, list[object]]] = []
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
        if self.__source_rows:
            self._view.set_target_rows(self.__source_rows)
        self.__sync_transfer_state()

    async def __load_source_bin(self, location: str) -> None:
        if not self._view:
            return
        source_bin = await self.__perform_get_single_bin(location)
        if not source_bin:
            self._view.set_source_bin_error(self._state_store.app_state.translation.items.get("bin_not_found"))
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            return
        if not source_bin.is_outbound:
            self._view.set_source_bin_error(self._state_store.app_state.translation.items.get("bin_not_outbound"))
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            return
        self.__source_bin = source_bin
        bin_items = await self.__perform_get_bin_items(source_bin.id)
        item_ids = [item.item_id for item in bin_items]
        item_schemas = await self.__perform_get_items_by_ids(item_ids)
        item_map = {item.id: item for item in item_schemas}
        self.__source_items = {}
        self.__source_bin_item_by_id = {}
        target_rows: list[tuple[int, list[object]]] = []
        for bin_item in bin_items:
            item_schema = item_map.get(bin_item.item_id)
            if item_schema:
                label: list[object] = [item_schema.index, item_schema.name, str(bin_item.quantity)]
            else:
                label: list[object] = [str(bin_item.item_id), "", str(bin_item.quantity)]
            self.__source_items[bin_item.item_id] = (str(label[0]), str(label[1]), bin_item.id, bin_item.quantity)
            self.__source_bin_item_by_id[bin_item.id] = bin_item.item_id
            target_rows.append((bin_item.id, label))
        self._view.set_target_rows(target_rows)
        self.__source_rows = target_rows
        self._view.set_target_enabled(True)
        self.__sync_transfer_state()

    def __sync_transfer_state(self) -> None:
        if not self._view:
            return
        source_enabled = any(remaining > 0 for remaining in self.__order_item_quantities.values()) or bool(
            self.__pending_move_item_ids
        )
        target_enabled = self.__source_bin is not None
        self._view.set_source_enabled(source_enabled)
        self._view.set_target_enabled(target_enabled)

    async def __handle_move_with_quantity(self, item_id: int, max_quantity: int) -> None:
        if not self._view:
            return
        await self.__ensure_item_label(item_id)
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
        if quantity > max_quantity:
            quantity = max_quantity
        source_item = self.__source_items.get(item_id)
        if not source_item:
            return
        _, _, bin_item_id, current_quantity = source_item
        new_pending = self.__pending_move_quantities.get(bin_item_id, 0) + quantity
        new_quantity = max(0, current_quantity - new_pending)
        self._view.update_existing_target(
            bin_item_id,
            item_id,
            [source_item[0], source_item[1], str(new_quantity)],
        )
        self.__pending_move_quantities[bin_item_id] = new_pending
        self.__pending_move_item_ids[bin_item_id] = item_id
        remaining = max(0, self.__order_item_quantities.get(item_id, 0) - quantity)
        self.__order_item_quantities[item_id] = remaining
        self.__refresh_source_rows()

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view or not self.__source_bin:
            return
        pending_targets = self._view.get_pending_targets()
        if not pending_targets:
            return
        updates: list[AssocBinItemStrictSchema] = []
        delete_ids: list[int] = []
        order_item_updates: list[AssocOrderItemStrictSchema] = []
        touched_item_ids: set[int] = set()
        moved_by_item: dict[int, int] = {}
        for target_id, item_id in pending_targets:
            move_quantity = self.__pending_move_quantities.get(target_id, 0)
            if move_quantity <= 0:
                continue
            mapped_item_id = self.__source_bin_item_by_id.get(target_id)
            source_item = self.__source_items.get(item_id)
            if not mapped_item_id or not source_item:
                continue
            _, _, bin_item_id, current_quantity = source_item
            new_quantity = max(0, current_quantity - move_quantity)
            if new_quantity > 0:
                updates.append(
                    AssocBinItemStrictSchema(
                        id=bin_item_id,
                        bin_id=self.__source_bin.id,
                        item_id=item_id,
                        quantity=new_quantity,
                    )
                )
            else:
                delete_ids.append(bin_item_id)
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
                    discount_id=order_item.discount_id,
                )
            )
        if updates:
            await self.__perform_update_bin_items(updates)
        if delete_ids:
            await self.__perform_delete_bin_items(delete_ids)
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
                new_stock = max(0, item_schema.stock_quantity - moved_quantity)
                update_tasks.append(
                    self.__perform_update_item(item_id, self.__build_item_update(item_schema, new_stock))
                )
            if update_tasks:
                await asyncio.gather(*update_tasks)
        if self.__source_bin is not None:
            await self.__load_source_bin(self.__source_bin.location)
        self.__pending_move_quantities.clear()
        self.__pending_move_item_ids.clear()
        if self.__current_order_id is not None:
            await self.__load_order_items(self.__current_order_id)
            await self.__maybe_update_order_status(self.__current_order_id, touched_item_ids)

    async def __maybe_update_order_status(self, order_id: int, touched_item_ids: set[int]) -> None:
        statuses = await self.__perform_get_all_statuses()
        status_by_order = {status.order: status for status in statuses}
        order_statuses = await self.__perform_get_order_statuses(order_id)
        if not order_statuses:
            return
        latest_status = max(order_statuses, key=lambda status: status.created_at)
        current_status = status_by_order.get(latest_status.status_id)
        if current_status is None:
            current_status = next((status for status in statuses if status.id == latest_status.status_id), None)
        current_order_value = current_status.order if current_status else None
        if current_order_value == 2 and touched_item_ids:
            next_status = status_by_order.get(3) or next((status for status in statuses if status.order == 3), None)
            if next_status:
                has_status = any(status.status_id == next_status.id for status in order_statuses)
                if not has_status:
                    await self.__perform_create_order_status(
                        AssocOrderStatusStrictSchema(order_id=order_id, status_id=next_status.id)
                    )
                current_order_value = 3
        order_items = await self.__perform_get_order_items(order_id)
        if order_items and any(item.to_process > 0 for item in order_items):
            return
        final_status = status_by_order.get(4) or next((status for status in statuses if status.order == 4), None)
        if not final_status:
            return
        if order_statuses:
            latest_status = max(order_statuses, key=lambda status: status.created_at)
            if latest_status.status_id == final_status.id:
                return
        await self.__perform_create_order_status(
            AssocOrderStatusStrictSchema(order_id=order_id, status_id=final_status.id)
        )

    def __refresh_source_rows(self) -> None:
        if not self._view:
            return
        source_rows: list[tuple[int, list[object]]] = []
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
        )
