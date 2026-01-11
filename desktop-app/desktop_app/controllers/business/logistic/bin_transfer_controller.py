import asyncio

import flet as ft
from httpx import HTTPStatusError

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.assoc_bin_item_schema import AssocBinItemPlainSchema, AssocBinItemStrictSchema
from schemas.business.logistic.bin_schema import BinPlainSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.bin_transfer_view import BinTransferView


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
        )

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

    async def __handle_bulk_transfer_save(self) -> None:
        if not self._view or not self.__target_bin:
            return
        pending_ids = self._view.get_pending_move_ids()
        if not pending_ids:
            return
        bin_items_schemas: list[AssocBinItemStrictSchema] = []
        for item_id in pending_ids:
            bin_items_schemas.append(
                AssocBinItemStrictSchema(
                    id=self.__source_items[item_id][1],
                    bin_id=self.__target_bin.id,
                    item_id=item_id,
                    quantity=self.__source_items[item_id][2],
                )
            )
        if not bin_items_schemas:
            return
        try:
            self._open_loading_dialog()
            await self.__move_items_to_target(bin_items_schemas)
            await self.__refresh_transfer_lists()
            self._close_loading_dialog()
        except HTTPStatusError as error:
            self._close_loading_dialog()
            self._open_error_dialog(message=str(error))
            self._close_loading_dialog()
        except Exception as error:
            self._open_error_dialog(message=str(error))

    async def __move_items_to_target(self, bin_items: list[AssocBinItemStrictSchema]) -> None:
        await self.__bin_item_service.call_api_with_token_refresh(
            func=self.__bin_item_service.update_many,
            endpoint=Endpoint.BIN_ITEMS,
            body_params=bin_items,
            module_id=self._module_id,
        )

    async def __refresh_transfer_lists(self) -> None:
        await asyncio.gather(self.__refresh_source_items(), self.__refresh_target_items())

    async def __refresh_source_items(self) -> None:
        if not self._view or not self.__source_bin:
            return
        translation_items = self._state_store.app_state.translation.items
        bin_schema = await self.__get_single_bin(self.__source_bin.location)
        if not bin_schema:
            self._view.set_source_items([])
            self._view.set_source_enabled(False)
            self._view.set_source_error(translation_items.get("bin_not_found"))
            self.__source_bin = None
            return
        self.__source_bin = bin_schema
        self.__source_items = await self.__fetch_bin_items(bin_schema)
        self._view.set_source_items([(key, value[0]) for key, value in self.__source_items.items()])
        self._view.set_source_enabled(True)
        self._view.set_source_error(None)

    async def __refresh_target_items(self) -> None:
        if not self._view or not self.__target_bin:
            return
        translation_items = self._state_store.app_state.translation.items
        bin_schema = await self.__get_single_bin(self.__target_bin.location)
        if not bin_schema:
            self._view.set_target_items([])
            self._view.set_target_enabled(False)
            self._view.set_target_error(translation_items.get("bin_not_found"))
            self.__target_bin = None
            return
        self.__target_bin = bin_schema
        self.__target_items = await self.__fetch_bin_items(bin_schema)
        self._view.set_target_items([(key, value[0]) for key, value in self.__target_items.items()])
        self._view.set_target_enabled(True)
        self._view.set_target_error(None)

    async def __validate_enable_and_load_source(self, location: str) -> None:
        if not self._view:
            return
        bin_schema = await self.__get_single_bin(location)
        if not bin_schema:
            self._view.set_source_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_source_error(translate_state.items.get("bin_not_found"))
            self.__source_bin = None
            return
        if self.__target_bin and bin_schema.id == self.__target_bin.id:
            self._view.set_target_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_target_error(translate_state.items.get("bins_must_be_different"))
            self.__source_bin = None
            return
        self.__source_bin = bin_schema
        self.__source_items = await self.__fetch_bin_items(bin_schema)
        self._view.set_source_items([(key, value[0]) for key, value in self.__source_items.items()])
        self._view.set_source_enabled(True)

    async def __validate_enable_and_load_target(self, location: str) -> None:
        if not self._view:
            return
        bin_schema = await self.__get_single_bin(location)
        if not bin_schema:
            self._view.set_target_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_target_error(translate_state.items.get("bin_not_found"))
            self.__target_bin = None
            return
        if self.__source_bin and bin_schema.id == self.__source_bin.id:
            self._view.set_target_enabled(False)
            translate_state = self._state_store.app_state.translation
            self._view.set_target_error(translate_state.items.get("bins_must_be_different"))
            self.__target_bin = None
            return
        self.__target_bin = bin_schema
        self.__target_items = await self.__fetch_bin_items(bin_schema)
        self._view.set_target_items([(key, value[0]) for key, value in self.__target_items.items()])
        self._view.set_target_enabled(True)

    async def __get_single_bin(self, location: str) -> BinPlainSchema | None:
        params = {"page": 1, "page_size": 2, "location": location}
        response = await self.__bin_service.call_api_with_token_refresh(
            func=self.__bin_service.get_page, endpoint=Endpoint.BINS, query_params=params, module_id=self._module_id
        )
        items = response.items
        exact_matches = [bin for bin in items if bin.location.lower() == location.lower()]
        if len(exact_matches) == 1:
            return exact_matches[0]
        return None

    async def __fetch_bin_items(self, bin: BinPlainSchema) -> dict[int, tuple[str, int, int]]:
        params = {"bin_id": bin.id, "sort_by": "id", "order": "asc"}
        bin_item_schemas = await self.__bin_item_service.call_api_with_token_refresh(
            func=self.__bin_item_service.get_all,
            endpoint=Endpoint.BIN_ITEMS,
            query_params=params,
            module_id=self._module_id,
        )
        if not bin_item_schemas:
            return {}

        source_items: dict[int, tuple[str, int, int]] = {}
        for bin_item in bin_item_schemas:
            item_schema = await self.__item_service.call_api_with_token_refresh(
                func=self.__item_service.get_one,
                endpoint=Endpoint.ITEMS,
                path_param=bin_item.item_id,
                module_id=self._module_id,
            )
            source_items[item_schema.id] = (item_schema.index, bin_item.id, bin_item.quantity)

        return source_items
