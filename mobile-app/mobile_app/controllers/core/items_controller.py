from __future__ import annotations

from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import MobileMainMenuRequested, ViewRequested
from schemas.business.logistic.category_schema import CategoryPlainSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.business.logistic import CategoryService, ItemService
from utils.enums import ApiActionError, Endpoint, View
from utils.translation import Translation
from views.core.items_view import ItemsView


class ItemsController(BaseViewController[ItemService, ItemsView, ItemPlainSchema, ItemStrictSchema]):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = ItemsView
    _view_key = View.ITEMS
    _endpoint = Endpoint.ITEMS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__category_service = CategoryService(self._settings, self._logger, self._tokens_accessor)

    def on_item_selected(
        self,
        item_id: int,
        quantity: int,
        selected_category_id: int | None,
        index_filter: str,
    ) -> None:
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=self._module_id,
                view_key=View.ITEMS,
                data={"item_id": item_id, "quantity": quantity},
                caller_view_key=View.ITEMS,
                caller_data={
                    "category_id": selected_category_id,
                    "index_filter": index_filter,
                },
            ),
        )

    def on_back_to_menu(self) -> None:
        self._page.run_task(self._event_bus.publish, MobileMainMenuRequested())

    def on_back_from_details(self) -> None:
        caller_view_key = self.caller_view_key
        caller_data = self.caller_data
        if caller_view_key == View.BINS:
            self._page.run_task(
                self._event_bus.publish,
                ViewRequested(
                    module_id=self._module_id,
                    view_key=View.BINS,
                    data=caller_data,
                ),
            )
            return
        if caller_view_key == View.ITEMS:
            self._page.run_task(
                self._event_bus.publish,
                ViewRequested(
                    module_id=self._module_id,
                    view_key=View.ITEMS,
                    data=caller_data,
                ),
            )
            return
        self.on_back_to_menu()

    async def _build_view(self, translation: Translation, event: ViewRequested) -> ItemsView:
        quantity = self.__resolve_quantity(event.data)
        item_id = self.__resolve_item_id(event.data)
        selected_category_id = self.__resolve_category_id(event.data)
        index_filter = self.__resolve_index_filter(event.data)

        categories = await self.__perform_get_all_categories()
        category_options = sorted(((schema.id, schema.name) for schema in categories), key=lambda item: item[1].lower())

        item: ItemPlainSchema | None = None
        items: list[ItemPlainSchema] = []

        if item_id is not None:
            fetched_item = await self._perform_get_one(item_id, self._service, self._endpoint)
            if fetched_item is not None:
                item_data = fetched_item.model_dump()
                self._normalize_data(item_data)
                item = ItemPlainSchema.model_validate(item_data)
                if quantity <= 0:
                    quantity = item.stock_quantity
        else:
            items = await self.__perform_get_all_items()
            items = sorted(items, key=lambda schema: (schema.index.lower(), schema.name.lower()))

        return ItemsView(
            controller=self,
            translation=translation,
            view_key=event.view_key,
            item=item,
            quantity=quantity,
            items=items,
            categories=category_options,
            selected_category_id=selected_category_id,
            index_filter=index_filter,
            caller_view_key=event.caller_view_key,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_categories(self) -> list[CategoryPlainSchema]:
        return await self.__category_service.get_all(Endpoint.CATEGORIES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_items(self) -> list[ItemPlainSchema]:
        query_params: dict[str, str] = {"sort_by": "index", "order": "asc"}
        return await self._service.get_all(Endpoint.ITEMS, None, query_params, None, self._module_id)

    @staticmethod
    def __resolve_item_id(data: dict[str, Any] | None) -> int | None:
        if not data:
            return None
        item_id = data.get("item_id")
        if isinstance(item_id, int):
            return item_id
        return None

    @staticmethod
    def __resolve_quantity(data: dict[str, Any] | None) -> int:
        if not data:
            return 0
        quantity = data.get("quantity")
        if isinstance(quantity, int):
            return quantity
        return 0

    @staticmethod
    def __resolve_category_id(data: dict[str, Any] | None) -> int | None:
        if not data:
            return None
        category_id = data.get("category_id")
        if isinstance(category_id, int):
            return category_id
        if isinstance(category_id, str):
            stripped = category_id.strip()
            if stripped in {"", "0"}:
                return None
            try:
                return int(stripped)
            except ValueError:
                return None
        return None

    @staticmethod
    def __resolve_index_filter(data: dict[str, Any] | None) -> str:
        if not data:
            return ""
        index_filter = data.get("index_filter")
        if isinstance(index_filter, str):
            return index_filter.strip()
        return ""
