from __future__ import annotations

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.business.logistic.bin_controller import BinController as DesktopBinController
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.logistic.bin_schema import BinPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.mobile.bins_view import BinsView


class BinsController(DesktopBinController):
    _view_cls = BinsView
    _view_key = View.BINS
    _endpoint = Endpoint.BINS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__bins: list[BinPlainSchema] = []
        self.__selected_bin: BinPlainSchema | None = None
        self.__items: list[ItemPlainSchema] = []
        self.__item_quantities: dict[int, int] = {}
        self.__bin_items_request_id = 0

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinsView:
        bins = await self.__perform_get_all_bins()
        if bins is None:
            bins = []
        self.__bins = sorted(bins, key=lambda schema: schema.location.lower())
        self.__selected_bin = None
        self.__items = []
        self.__item_quantities = {}
        self.__bin_items_request_id = 0

        view = BinsView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
        )
        view.set_bins(self.__bins)

        selected_bin_id = self.__resolve_selected_bin_id(event.data)
        if selected_bin_id is None:
            return view
        selected_bin = next((schema for schema in self.__bins if schema.id == selected_bin_id), None)
        if not selected_bin:
            return view
        await self.__set_selected_bin_items(selected_bin)
        view.set_bin_items(
            bin_schema=self.__selected_bin,
            items=self.__items,
            item_quantities=self.__item_quantities,
        )
        return view

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
                mode=ViewMode.STATIC,
                data={"item_id": item_id, "quantity": quantity},
                caller_view_key=View.BINS,
                caller_data={"selected_bin_id": self.__selected_bin.id},
            ),
        )

    async def __load_items_for_bin(self, bin_id: int, request_id: int) -> None:
        selected_bin = next((schema for schema in self.__bins if schema.id == bin_id), None)
        if not selected_bin:
            return
        await self.__set_selected_bin_items(selected_bin)
        if request_id != self.__bin_items_request_id:
            return
        if not isinstance(self._view, BinsView):
            return
        self._view.set_bin_items(
            bin_schema=self.__selected_bin,
            items=self.__items,
            item_quantities=self.__item_quantities,
        )
        self._page.update()

    async def __set_selected_bin_items(self, selected_bin: BinPlainSchema) -> None:
        item_quantities = await self._perform_get_bin_item_quantities(selected_bin.id)
        item_ids = sorted(item_quantities.keys())
        items = await self._perform_get_items_for_ids(item_ids) if item_ids else []
        self.__selected_bin = selected_bin
        self.__items = sorted(items, key=lambda schema: schema.name.lower())
        self.__item_quantities = item_quantities

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_bins(self) -> list[BinPlainSchema]:
        return await self._service.get_all(self._endpoint, None, None, None, self._module_id)

    @staticmethod
    def __resolve_selected_bin_id(data: dict[str, object] | None) -> int | None:
        if not data:
            return None
        selected_bin_id = data.get("selected_bin_id")
        if isinstance(selected_bin_id, int):
            return selected_bin_id
        return None
