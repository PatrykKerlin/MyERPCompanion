from __future__ import annotations

from controllers.business.logistic.item_controller import ItemController as DesktopItemController
from events.events import ViewRequested
from schemas.business.logistic.item_schema import ItemPlainSchema
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.mobile.items_view import ItemsView


class ItemsController(DesktopItemController):
    _view_cls = ItemsView
    _view_key = View.ITEMS
    _endpoint = Endpoint.ITEMS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemsView:
        quantity = self.__resolve_quantity(event.data)
        item_id = self.__resolve_item_id(event.data)
        item = None
        if item_id is not None:
            item = await self._perform_get_one(item_id, self._service, self._endpoint)
            if item is not None:
                item_data = item.model_dump()
                self._parse_data_row(item_data)
                item = ItemPlainSchema.model_validate(item_data)
        return ItemsView(
            controller=self,
            translation=translation,
            mode=ViewMode.STATIC,
            view_key=event.view_key,
            data_row=event.data,
            item=item,
            quantity=quantity,
        )

    def on_back_to_bins(self) -> None:
        caller_data = self.search_params.caller_data if isinstance(self.search_params.caller_data, dict) else None
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=self._module_id,
                view_key=View.BINS,
                mode=ViewMode.STATIC,
                data=caller_data,
            ),
        )

    @staticmethod
    def __resolve_item_id(data: dict[str, object] | None) -> int | None:
        if not data:
            return None
        item_id = data.get("item_id")
        if isinstance(item_id, int):
            return item_id
        return None

    @staticmethod
    def __resolve_quantity(data: dict[str, object] | None) -> int:
        if not data:
            return 0
        quantity = data.get("quantity")
        if isinstance(quantity, int):
            return quantity
        return 0
