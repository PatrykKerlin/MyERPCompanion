from __future__ import annotations

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.mobile.bin_transfer_view import BinTransferView


class BinTransferController(
    BaseViewController[AssocBinItemService, BinTransferView, AssocBinItemPlainSchema, AssocBinItemStrictSchema]
):
    _plain_schema_cls = AssocBinItemPlainSchema
    _strict_schema_cls = AssocBinItemStrictSchema
    _service_cls = AssocBinItemService
    _view_cls = BinTransferView
    _endpoint = Endpoint.BIN_ITEMS
    _view_key = View.BIN_TRANSFER

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__bin_item_service = self._service
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)

        self.__source_bin: BinPlainSchema | None = None
        self.__target_bin: BinPlainSchema | None = None
        self.__source_items: dict[int, tuple[str, int, int]] = {}
        self.__target_items: dict[int, tuple[str, int, int]] = {}
        self.__pending_move_quantities: dict[int, int] = {}

        self.__source_request_id = 0
        self.__target_request_id = 0

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinTransferView:
        self.__source_bin = None
        self.__target_bin = None
        self.__source_items = {}
        self.__target_items = {}
        self.__pending_move_quantities = {}
        self.__source_request_id = 0
        self.__target_request_id = 0

        return BinTransferView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
        )

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_source_bin_submit(self, location_value: str) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        location = location_value.strip()
        if not location:
            self._view.set_source_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_source_error(None)
        self.__source_request_id += 1
        request_id = self.__source_request_id
        self._page.run_task(self.__validate_and_load_source_bin, location, request_id)

    def on_target_bin_submit(self, location_value: str) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        location = location_value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self.__target_request_id += 1
        request_id = self.__target_request_id
        self._page.run_task(self.__validate_and_load_target_bin, location, request_id)

    def on_add_clicked(self, item_id: int | None, quantity: int | None) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        if self.__source_bin is None or self.__target_bin is None:
            self._open_error_dialog(message_key="value_required")
            return
        if item_id is None or quantity is None:
            self._open_error_dialog(message_key="value_required")
            return
        if quantity <= 0:
            self._open_error_dialog(message_key="value_required")
            return

        source_item = self.__source_items.get(item_id)
        if not source_item:
            self._open_error_dialog(message_key="value_required")
            return

        source_quantity = source_item[2]
        pending_quantity = self.__pending_move_quantities.get(item_id, 0)
        remaining_quantity = source_quantity - pending_quantity
        if remaining_quantity <= 0:
            return

        bounded_quantity = min(quantity, remaining_quantity)
        if bounded_quantity <= 0:
            return
        self.__pending_move_quantities[item_id] = pending_quantity + bounded_quantity
        self.__sync_view_state()

    def on_pending_item_removed(self, item_id: int) -> None:
        if item_id in self.__pending_move_quantities:
            self.__pending_move_quantities.pop(item_id, None)
            self.__sync_view_state()

    def on_save_clicked(self) -> None:
        self._page.run_task(self.__handle_save)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.create_bulk(
            Endpoint.BIN_ITEMS_CREATE_BULK,
            None,
            None,
            items,
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.update_bulk(
            Endpoint.BIN_ITEMS_UPDATE_BULK,
            None,
            None,
            items,
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_source_items(self, ids: list[int]) -> None:
        body_params = IdsPayloadSchema(ids=ids)
        await self.__bin_item_service.delete_bulk(
            Endpoint.BIN_ITEMS_DELETE_BULK,
            None,
            None,
            body_params,
            self._module_id,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_single_bin(self, location: str) -> BinPlainSchema | None:
        query_params = {"page": 1, "page_size": 2, "location": location}
        response = await self.__bin_service.get_page(
            Endpoint.BINS,
            None,
            query_params,
            None,
            self._module_id,
        )
        exact_matches = [bin_schema for bin_schema in response.items if bin_schema.location.lower() == location.lower()]
        if len(exact_matches) == 1:
            return exact_matches[0]
        return None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_fetch_bin_items(self, bin_schema: BinPlainSchema) -> dict[int, tuple[str, int, int]]:
        if not bin_schema.item_ids:
            return {}

        body_params = IdsPayloadSchema(ids=bin_schema.item_ids)
        item_schemas = await self.__item_service.get_bulk(
            Endpoint.ITEMS_GET_BULK,
            None,
            None,
            body_params,
            self._module_id,
        )
        if not item_schemas:
            return {}
        item_map = {item.id: item for item in item_schemas}

        query_params = {"bin_id": bin_schema.id}
        bin_item_schemas = await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS,
            None,
            query_params,
            None,
            self._module_id,
        )
        if not bin_item_schemas:
            return {}

        items: dict[int, tuple[str, int, int]] = {}
        for bin_item in bin_item_schemas:
            item_schema = item_map.get(bin_item.item_id)
            if item_schema is None:
                continue
            items[item_schema.id] = (item_schema.index, bin_item.id, bin_item.quantity)
        return items

    async def __validate_and_load_source_bin(self, location: str, request_id: int) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        await self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        bin_schema = await self.__perform_get_single_bin(location)
        if request_id != self.__source_request_id:
            self._close_loading_dialog()
            return
        if bin_schema is None:
            self.__source_bin = None
            self.__source_items = {}
            self.__pending_move_quantities.clear()
            self._close_loading_dialog()
            self._view.set_source_error(translation.get("bin_not_found"))
            self.__sync_view_state()
            return

        if self.__target_bin is not None and bin_schema.id == self.__target_bin.id:
            self.__source_bin = None
            self.__source_items = {}
            self.__pending_move_quantities.clear()
            self._close_loading_dialog()
            self._view.set_source_error(translation.get("bins_must_be_different"))
            self.__sync_view_state()
            return

        self.__source_bin = bin_schema
        self.__source_items = await self.__perform_fetch_bin_items(bin_schema) or {}
        self.__sanitize_pending_moves()
        self._close_loading_dialog()
        self._view.set_source_error(None)
        self.__sync_view_state()

    async def __validate_and_load_target_bin(self, location: str, request_id: int) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        await self._open_loading_dialog()
        translation = self._state_store.app_state.translation.items
        bin_schema = await self.__perform_get_single_bin(location)
        if request_id != self.__target_request_id:
            self._close_loading_dialog()
            return
        if bin_schema is None:
            self.__target_bin = None
            self.__target_items = {}
            self._close_loading_dialog()
            self._view.set_target_error(translation.get("bin_not_found"))
            self.__sync_view_state()
            return

        if self.__source_bin is not None and bin_schema.id == self.__source_bin.id:
            self.__target_bin = None
            self.__target_items = {}
            self._close_loading_dialog()
            self._view.set_target_error(translation.get("bins_must_be_different"))
            self.__sync_view_state()
            return

        self.__target_bin = bin_schema
        self.__target_items = await self.__perform_fetch_bin_items(bin_schema) or {}
        self._close_loading_dialog()
        self._view.set_target_error(None)
        self.__sync_view_state()

    async def __handle_save(self) -> None:
        if self.__source_bin is None or self.__target_bin is None:
            self._open_error_dialog(message_key="value_required")
            return
        if not self.__pending_move_quantities:
            self._open_error_dialog(message_key="value_required")
            return

        updates: list[AssocBinItemStrictSchema] = []
        creates: list[AssocBinItemStrictSchema] = []
        delete_ids: list[int] = []

        for item_id, move_quantity in self.__pending_move_quantities.items():
            source_item = self.__source_items.get(item_id)
            if source_item is None:
                continue
            _source_index, source_bin_item_id, source_quantity = source_item
            bounded_quantity = max(1, min(move_quantity, source_quantity))
            target_item = self.__target_items.get(item_id)

            if target_item is not None:
                target_bin_item_id = target_item[1]
                target_quantity = target_item[2]
                updates.append(
                    AssocBinItemStrictSchema(
                        id=target_bin_item_id,
                        bin_id=self.__target_bin.id,
                        item_id=item_id,
                        quantity=target_quantity + bounded_quantity,
                    )
                )
                if bounded_quantity < source_quantity:
                    updates.append(
                        AssocBinItemStrictSchema(
                            id=source_bin_item_id,
                            bin_id=self.__source_bin.id,
                            item_id=item_id,
                            quantity=source_quantity - bounded_quantity,
                        )
                    )
                else:
                    delete_ids.append(source_bin_item_id)
                continue

            if bounded_quantity < source_quantity:
                creates.append(
                    AssocBinItemStrictSchema(
                        bin_id=self.__target_bin.id,
                        item_id=item_id,
                        quantity=bounded_quantity,
                    )
                )
                updates.append(
                    AssocBinItemStrictSchema(
                        id=source_bin_item_id,
                        bin_id=self.__source_bin.id,
                        item_id=item_id,
                        quantity=source_quantity - bounded_quantity,
                    )
                )
                continue

            updates.append(
                AssocBinItemStrictSchema(
                    id=source_bin_item_id,
                    bin_id=self.__target_bin.id,
                    item_id=item_id,
                    quantity=source_quantity,
                )
            )

        if not updates and not creates and not delete_ids:
            self._open_error_dialog(message_key="value_required")
            return

        if creates:
            await self.__perform_create_bin_items(creates)
        if updates:
            await self.__perform_update_bin_items(updates)
        if delete_ids:
            await self.__perform_delete_source_items(delete_ids)

        await self.__refresh_loaded_bins()
        self.__pending_move_quantities.clear()
        self.__sync_view_state()

    async def __refresh_loaded_bins(self) -> None:
        if self.__source_bin is not None:
            refreshed_source = await self.__perform_get_single_bin(self.__source_bin.location)
            if refreshed_source is None:
                self.__source_bin = None
                self.__source_items = {}
                self.__pending_move_quantities.clear()
            else:
                self.__source_bin = refreshed_source
                self.__source_items = await self.__perform_fetch_bin_items(refreshed_source) or {}
        if self.__target_bin is not None:
            refreshed_target = await self.__perform_get_single_bin(self.__target_bin.location)
            if refreshed_target is None:
                self.__target_bin = None
                self.__target_items = {}
            else:
                self.__target_bin = refreshed_target
                self.__target_items = await self.__perform_fetch_bin_items(refreshed_target) or {}
        self.__sanitize_pending_moves()

    def __sanitize_pending_moves(self) -> None:
        sanitized: dict[int, int] = {}
        for item_id, requested_quantity in self.__pending_move_quantities.items():
            source_item = self.__source_items.get(item_id)
            if source_item is None:
                continue
            source_quantity = source_item[2]
            bounded_quantity = max(0, min(requested_quantity, source_quantity))
            if bounded_quantity > 0:
                sanitized[item_id] = bounded_quantity
        self.__pending_move_quantities = sanitized

    def __sync_view_state(self) -> None:
        if not isinstance(self._view, BinTransferView):
            return
        source_rows: list[tuple[int, str, int]] = []
        for item_id, (item_index, _source_bin_item_id, source_quantity) in self.__source_items.items():
            pending_quantity = self.__pending_move_quantities.get(item_id, 0)
            remaining_quantity = source_quantity - pending_quantity
            if remaining_quantity <= 0:
                continue
            source_rows.append((item_id, item_index, remaining_quantity))
        source_rows.sort(key=lambda row: row[1].lower())

        pending_rows: list[tuple[int, str, int]] = []
        for item_id, pending_quantity in self.__pending_move_quantities.items():
            source_item = self.__source_items.get(item_id)
            if source_item is None:
                continue
            pending_rows.append((item_id, source_item[0], pending_quantity))
        pending_rows.sort(key=lambda row: row[1].lower())

        can_add = self.__source_bin is not None and self.__target_bin is not None and bool(source_rows)
        can_save = self.__source_bin is not None and self.__target_bin is not None and bool(pending_rows)

        self._view.set_source_items(source_rows)
        self._view.set_pending_items(pending_rows)
        self._view.set_form_enabled(can_add)
        self._view.set_save_enabled(can_save)
