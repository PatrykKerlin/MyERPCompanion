from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from controllers.controls.dual_assign_controller import DualAssignController
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.bin_transfer_view import BinTransferView
from events.events import ViewRequested
from typing import Any
import flet as ft


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
        self.__dual_assign_controller = DualAssignController()
        self.__bin_item_service = self._service
        self.__bin_service = BinService(self._settings, self._logger, self._tokens_accessor)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__source_bin: BinPlainSchema | None = None
        self.__target_bin: BinPlainSchema | None = None

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        await self._handle_view_requested(event)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinTransferView:
        mode = ViewMode.STATIC
        return BinTransferView(
            self,
            translation,
            mode,
            event.view_key,
            self.__dual_assign_controller,
            self.on_source_bin_submit,
            self.on_target_bin_submit,
        )

    def on_source_bin_submit(self, event: ft.ControlEvent) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_source_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_source_error(None)
        self._page.run_task(self.__validate_enable_and_load_source, location)

    def on_target_bin_submit(self, event: ft.ControlEvent) -> None:
        if not self._view:
            return
        location = event.control.value.strip()
        if not location:
            self._view.set_target_error(self._state_store.app_state.translation.items.get("value_required"))
            return
        self._view.set_target_error(None)
        self._page.run_task(self.__validate_enable_and_load_target, location)

    async def __validate_enable_and_load_source(self, location: str) -> None:
        if not self._view:
            return
        bin = await self.__get_single_bin(location)
        if not bin:
            self._view.set_source_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_source_error(translate_state.items.get("bin_not_found"))
            self.__source_bin = None
            return
        if self.__source_bin and bin.id == self.__source_bin.id:
            translate_state = self._state_store.app_state.translation
            self._view.set_target_enabled(False)
            self._view.set_target_error(translate_state.items.get("bins_must_be_different"))
            self.__source_bin = None
            return
        self.__source_bin = bin
        items = await self.__fetch_bin_items(bin)
        self._view.set_source_items(items)
        self._view.set_source_enabled(True)

    async def __validate_enable_and_load_target(self, location: str) -> None:
        if not self._view:
            return
        bin = await self.__get_single_bin(location)
        if not bin:
            self._view.set_target_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_target_error(translate_state.items.get("bin_not_found"))
            self.__target_bin = None
            return
        if self.__source_bin and bin.id == self.__source_bin.id:
            translate_state = self._state_store.app_state.translation
            self._view.set_target_enabled(False)
            self._view.set_target_error(translate_state.items.get("bins_must_be_different"))
            self.__target_bin = None
            return
        self.__target_bin = bin
        items = await self.__fetch_bin_items(bin)
        self._view.set_target_items(items)
        self._view.set_target_enabled(True)

    async def __get_single_bin(self, location: str) -> BinPlainSchema | None:
        params: dict[str, Any] = {"page": 1, "page_size": 2, "location": location}
        response = await self.__bin_service.call_api_with_token_refresh(
            func=self.__bin_service.get_page, endpoint=Endpoint.BINS, query_params=params, module_id=self._module_id
        )
        items = response.items
        exact_matches = [bin for bin in items if bin.location.lower() == location.lower()]
        if len(exact_matches) == 1:
            return exact_matches[0]
        return None

    async def __fetch_bin_items(self, bin: BinPlainSchema) -> list[tuple[int, str]]:
        if len(bin.item_ids) == 0:
            return []
        items = await self.__item_service.call_api_with_token_refresh(
            func=self.__item_service.post_many,
            endpoint=Endpoint.ITEMS,
            body_params={"ids": bin.item_ids},
            module_id=self._module_id,
        )
        return [(int(obj.id), str(obj.index)) for obj in items]
