import asyncio

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.bin_transfer_view import BinTransferView
from views.components.quantity_dialog_component import QuantityDialogComponent


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

    def on_source_bin_submit(self, event: ft.Event[ft.TextField]) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_source_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_source_error(None)
        self._page.run_task(self.__validate_enable_and_load_source, location)

    def on_target_bin_submit(self, event: ft.Event[ft.TextField]) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self._page.run_task(self.__validate_enable_and_load_target, location)

    def on_bulk_transfer_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_bulk_transfer_save)

    def on_bulk_transfer_move_requested(self, selected_ids: list[int]) -> None:
        if not self._view or not selected_ids:
            return
        item_id = selected_ids[0]
        source_item = self.__source_items.get(item_id)
        if not source_item:
            return
        max_quantity = source_item[2]
        self._page.run_task(self.__handle_move_with_quantity, item_id, max_quantity)

    def on_bulk_transfer_pending_reverted(self, item_ids: list[int]) -> None:
        for item_id in item_ids:
            self.__pending_move_quantities.pop(item_id, None)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinTransferView:
        mode = ViewMode.STATIC
        return BinTransferView(
            self,
            translation,
            mode,
            event.view_key,
            self.on_source_bin_submit,
            self.on_target_bin_submit,
            self.on_bulk_transfer_save_clicked,
            self.on_bulk_transfer_move_requested,
            self.on_bulk_transfer_pending_reverted,
        )

    async def __perform_create_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.create_bulk(Endpoint.BIN_ITEMS_CREATE_BULK, None, None, items, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_bin_items(self, items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.update_bulk(Endpoint.BIN_ITEMS_UPDATE_BULK, None, None, items, self._module_id)

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_source_items(self, ids: list[int]) -> None:
        body_params = IdsPayloadSchema(ids=ids)
        await self.__bin_item_service.delete_bulk(
            Endpoint.BIN_ITEMS_DELETE_BULK, None, None, body_params, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_single_bin(self, location: str) -> BinPlainSchema | None:
        query_params = {"page": 1, "page_size": 2, "location": location}
        response = await self.__bin_service.get_page(Endpoint.BINS, None, query_params, None, self._module_id)
        items = response.items
        exact_matches = [bin for bin in items if bin.location.lower() == location.lower()]
        if len(exact_matches) == 1:
            return exact_matches[0]
        return None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_fetch_bin_items(self, bin: BinPlainSchema) -> dict[int, tuple[str, int, int]]:
        if not bin.item_ids:
            return {}
        body_params = IdsPayloadSchema(ids=bin.item_ids)
        item_schemas = await self.__item_service.get_bulk(
            Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id
        )
        item_map = {item.id: item for item in item_schemas}
        query_params = {"bin_id": bin.id}
        bin_item_schemas = await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, query_params, None, self._module_id
        )
        if not bin_item_schemas:
            return {}

        source_items: dict[int, tuple[str, int, int]] = {}
        for bin_item in bin_item_schemas:
            item_schema = item_map.get(bin_item.item_id)
            if not item_schema:
                continue
            source_items[item_schema.id] = (item_schema.index, bin_item.id, bin_item.quantity)

        return source_items

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view or not self.__target_bin or not self.__source_bin:
            return
        pending_ids = self._view.get_pending_move_ids()
        if not pending_ids:
            return
        updates: list[AssocBinItemStrictSchema] = []
        creates: list[AssocBinItemStrictSchema] = []
        delete_ids: list[int] = []
        for item_id in pending_ids:
            source_item = self.__source_items[item_id]
            source_bin_item_id = source_item[1]
            source_quantity = source_item[2]
            move_quantity = self.__pending_move_quantities.get(item_id, source_quantity)
            move_quantity = max(1, min(move_quantity, source_quantity))
            target_item = self.__target_items.get(item_id)
            if target_item:
                target_bin_item_id = target_item[1]
                target_quantity = target_item[2]
                updates.append(
                    AssocBinItemStrictSchema(
                        id=target_bin_item_id,
                        bin_id=self.__target_bin.id,
                        item_id=item_id,
                        quantity=target_quantity + move_quantity,
                    )
                )
                if move_quantity < source_quantity:
                    updates.append(
                        AssocBinItemStrictSchema(
                            id=source_bin_item_id,
                            bin_id=self.__source_bin.id,
                            item_id=item_id,
                            quantity=source_quantity - move_quantity,
                        )
                    )
                else:
                    delete_ids.append(source_bin_item_id)
            else:
                if move_quantity < source_quantity:
                    creates.append(
                        AssocBinItemStrictSchema(
                            bin_id=self.__target_bin.id,
                            item_id=item_id,
                            quantity=move_quantity,
                        )
                    )
                    updates.append(
                        AssocBinItemStrictSchema(
                            id=source_bin_item_id,
                            bin_id=self.__source_bin.id,
                            item_id=item_id,
                            quantity=source_quantity - move_quantity,
                        )
                    )
                else:
                    updates.append(
                        AssocBinItemStrictSchema(
                            id=source_bin_item_id,
                            bin_id=self.__target_bin.id,
                            item_id=item_id,
                            quantity=source_quantity,
                        )
                    )
        if not updates and not creates:
            return
        if creates:
            await self.__perform_create_bin_items(creates)
        if updates:
            await self.__perform_update_bin_items(updates)
        if delete_ids:
            await self.__perform_delete_source_items(delete_ids)
        await self.__refresh_transfer_lists()
        self.__pending_move_quantities.clear()

    async def __handle_move_with_quantity(self, item_id: int, max_quantity: int) -> None:
        if not self._view:
            return
        quantity = await self.__show_quantity_dialog(max_quantity)
        if not quantity:
            return
        self.__pending_move_quantities[item_id] = quantity
        source_item = self.__source_items.get(item_id)
        if not source_item:
            return
        target_item = self.__target_items.get(item_id)
        if target_item:
            display_quantity = target_item[2] + quantity
            self._view.update_existing_target(item_id, item_id, [source_item[0], str(display_quantity)])
            return
        self._view.add_target_row(item_id, [source_item[0], str(quantity)], highlight=True)

    async def __show_quantity_dialog(self, max_quantity: int) -> int | None:
        translation = self._state_store.app_state.translation.items
        dialog = QuantityDialogComponent(translation, max_quantity, default_value=max_quantity, min_value=1)
        try:
            await self._show_dialog_serialized(dialog, wait_for_future=dialog.future)
            return await dialog.future
        finally:
            self._page.pop_dialog()

    async def __refresh_transfer_lists(self) -> None:
        await asyncio.gather(self.__refresh_source_items(), self.__refresh_target_items())

    async def __refresh_source_items(self) -> None:
        if not self._view or not self.__source_bin:
            return
        translation = self._state_store.app_state.translation.items
        bin_schema = await self.__perform_get_single_bin(self.__source_bin.location)
        if not bin_schema:
            self._view.set_source_rows([])
            self._view.set_source_enabled(False)
            self._view.set_source_error(translation.get("bin_not_found"))
            self.__source_bin = None
            return
        self.__source_bin = bin_schema
        self.__source_items = await self.__perform_fetch_bin_items(bin_schema)
        self._view.set_source_rows([(key, [value[0], str(value[2])]) for key, value in self.__source_items.items()])
        self._view.set_source_enabled(True)
        self._view.set_source_error(None)

    async def __refresh_target_items(self) -> None:
        if not self._view or not self.__target_bin:
            return
        translation = self._state_store.app_state.translation.items
        bin_schema = await self.__perform_get_single_bin(self.__target_bin.location)
        if not bin_schema:
            self._view.set_target_rows([])
            self._view.set_target_enabled(False)
            self._view.set_target_error(translation.get("bin_not_found"))
            self.__target_bin = None
            return
        self.__target_bin = bin_schema
        self.__target_items = await self.__perform_fetch_bin_items(bin_schema)
        self._view.set_target_rows([(key, [value[0], str(value[2])]) for key, value in self.__target_items.items()])
        self._view.set_target_enabled(True)
        self._view.set_target_error(None)

    async def __validate_enable_and_load_source(self, location: str) -> None:
        if not self._view:
            return
        await self._open_loading_dialog()
        bin_schema = await self.__perform_get_single_bin(location)
        if not bin_schema:
            self._close_loading_dialog()
            self._view.set_source_enabled(False)
            translate = self._state_store.app_state.translation.items
            self._view.set_source_error(translate.get("bin_not_found"))
            self.__source_bin = None
            return
        if self.__target_bin and bin_schema.id == self.__target_bin.id:
            self._close_loading_dialog()
            self._view.set_target_enabled(False)
            translate = self._state_store.app_state.translation.items
            self._view.set_target_error(translate.get("bins_must_be_different"))
            self.__source_bin = None
            return
        self.__source_bin = bin_schema
        self.__source_items = await self.__perform_fetch_bin_items(bin_schema)
        self._close_loading_dialog()
        self._view.set_source_rows([(key, [value[0], str(value[2])]) for key, value in self.__source_items.items()])
        self._view.set_source_enabled(True)

    async def __validate_enable_and_load_target(self, location: str) -> None:
        if not self._view:
            return
        await self._open_loading_dialog()
        bin_schema = await self.__perform_get_single_bin(location)
        if not bin_schema:
            self._close_loading_dialog()
            self._view.set_target_enabled(False)
            translate = self._state_store.app_state.translation.items
            self._view.set_target_error(translate.get("bin_not_found"))
            self.__target_bin = None
            return
        if self.__source_bin and bin_schema.id == self.__source_bin.id:
            self._close_loading_dialog()
            self._view.set_target_enabled(False)
            translate = self._state_store.app_state.translation.items
            self._view.set_target_error(translate.get("bins_must_be_different"))
            self.__target_bin = None
            return
        self.__target_bin = bin_schema
        self.__target_items = await self.__perform_fetch_bin_items(bin_schema)
        self._close_loading_dialog()
        self._view.set_target_rows([(key, [value[0], str(value[2])]) for key, value in self.__target_items.items()])
        self._view.set_target_enabled(True)
