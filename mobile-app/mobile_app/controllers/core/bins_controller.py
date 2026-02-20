from __future__ import annotations

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import AssocBinItemService, BinService, ItemService
from utils.enums import ApiActionError, Endpoint, View
from utils.translation import Translation
from views.core.bins_view import BinsView


class BinsController(BaseViewController[BinService, BinsView, BinPlainSchema, BinStrictSchema]):
    _plain_schema_cls = BinPlainSchema
    _strict_schema_cls = BinStrictSchema
    _service_cls = BinService
    _view_cls = BinsView
    _view_key = View.BINS
    _endpoint = Endpoint.BINS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__bin_item_service = AssocBinItemService(self._settings, self._logger, self._tokens_accessor)
        self.__bins: list[BinPlainSchema] = []
        self.__selected_bin: BinPlainSchema | None = None
        self.__items: list[ItemPlainSchema] = []
        self.__item_quantities: dict[int, int] = {}
        self.__bin_items_request_id = 0

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_bin_selected(self, bin_id: int) -> None:
        self.__bin_items_request_id += 1
        request_id = self.__bin_items_request_id
        self._page.run_task(self.__load_items_for_bin, bin_id, request_id)

    def on_item_selected(self, item_id: int) -> None:
        if not self.__selected_bin:
            return
        quantity = self.__item_quantities.get(item_id, 0)
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=self._module_id,
                view_key=View.ITEMS,
                data={"item_id": item_id, "quantity": quantity},
                caller_view_key=View.BINS,
                caller_data={"selected_bin_id": self.__selected_bin.id},
            ),
        )

    async def _build_view(self, translation: Translation, event: ViewRequested) -> BinsView:
        bins = await self.__perform_get_all_bins()
        selected_warehouse_id = self._get_mobile_selected_warehouse_id()
        if selected_warehouse_id is not None:
            bins = [schema for schema in bins if schema.warehouse_id == selected_warehouse_id]
        self.__bins = sorted(bins, key=lambda schema: schema.location.lower())
        self.__selected_bin = None
        self.__items = []
        self.__item_quantities = {}
        self.__bin_items_request_id = 0

        view = BinsView(
            controller=self,
            translation=translation,
            view_key=event.view_key,
        )
        view.set_bins(self.__bins)
        selected_bin_id = event.data.get("selected_bin_id") if event.data else None
        if selected_bin_id is None:
            return view
        selected_bin = next((schema for schema in self.__bins if schema.id == selected_bin_id), None)
        if selected_bin is None:
            return view
        await self.__set_selected_bin_items(selected_bin)
        selected_bin_schema = self.__selected_bin
        if selected_bin_schema is None:
            return view
        view.set_bin_items(
            bin_schema=selected_bin_schema,
            items=self.__items,
            item_quantities=self.__item_quantities,
        )
        return view

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_bins(self) -> list[BinPlainSchema]:
        return await self._service.get_all(self._endpoint, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_items_for_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        if not item_ids:
            return []
        body_params = IdsPayloadSchema(ids=item_ids)
        return await self.__item_service.get_bulk(Endpoint.ITEMS_GET_BULK, None, None, body_params, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_bin_item_quantities(self, bin_id: int) -> dict[int, int]:
        query_params = {"bin_id": bin_id}
        bin_item_schemas = await self.__bin_item_service.get_all(
            Endpoint.BIN_ITEMS, None, query_params, None, self._module_id
        )
        return {schema.item_id: schema.quantity for schema in bin_item_schemas}

    async def __load_items_for_bin(self, bin_id: int, request_id: int) -> None:
        selected_bin = next((schema for schema in self.__bins if schema.id == bin_id), None)
        if not selected_bin:
            return
        await self.__set_selected_bin_items(selected_bin)
        if request_id != self.__bin_items_request_id:
            return
        if not isinstance(self._view, BinsView):
            return
        selected_bin_schema = self.__selected_bin
        if selected_bin_schema is None:
            return
        self._view.set_bin_items(
            bin_schema=selected_bin_schema,
            items=self.__items,
            item_quantities=self.__item_quantities,
        )
        self._page.update()

    async def __set_selected_bin_items(self, selected_bin: BinPlainSchema) -> None:
        item_quantities = await self.__perform_get_bin_item_quantities(selected_bin.id)
        item_ids = sorted(item_quantities.keys())
        items = await self.__perform_get_items_for_ids(item_ids)
        self.__selected_bin = selected_bin
        self.__items = sorted(items, key=lambda schema: schema.name.lower())
        self.__item_quantities = item_quantities
