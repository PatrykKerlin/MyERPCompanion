from __future__ import annotations

from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested, CartUpdated
from schemas.business.trade.order_view_schema import OrderViewResponseSchema, OrderViewSourceItemSchema
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.business.logistic import ItemService
from services.business.trade import OrderViewService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from utils.media_url import normalize_media_url
from views.web.create_order_view import CreateOrderView

from config.context import Context


class CreateOrderController(
    BaseViewController[ItemService, CreateOrderView, ItemPlainSchema, ItemStrictSchema],
):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = CreateOrderView
    _endpoint = Endpoint.ITEMS
    _view_key = View.WEB_CREATE_ORDER

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_view_service = OrderViewService(self._settings, self._logger, self._tokens_accessor)
        self.__cart: dict[int, dict[str, int | None]] = {}

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CreateOrderView:
        view_data = await self.__perform_get_sales_view()
        self._logger.info(
            "CreateOrderView data: module_id=%s categories=%s source_items=%s",
            self._module_id,
            len(view_data.categories),
            len(view_data.source_items),
        )
        image_map, images_map = self.__build_image_maps(view_data.source_items)
        return CreateOrderView(
            controller=self,
            translation=translation,
            categories=view_data.categories,
            items=view_data.source_items,
            image_map=image_map,
            images_map=images_map,
        )

    def on_add_to_cart(
        self,
        item_id: int,
        quantity: int,
        category_id: int | None,
        category_discount_id: int | None,
        item_discount_id: int | None,
    ) -> None:
        if quantity <= 0:
            return
        self.__cart[item_id] = {
            "quantity": quantity,
            "category_id": category_id,
            "category_discount_id": category_discount_id,
            "item_discount_id": item_discount_id,
        }
        total = sum(int(value["quantity"]) for value in self.__cart.values() if value.get("quantity"))
        self._page.run_task(self._event_bus.publish, CartUpdated(count=total))

    def on_category_discount_changed(self, category_id: int, selected_value: str) -> None:
        category_discount_id = None
        if selected_value and selected_value != "0":
            try:
                category_discount_id = int(selected_value)
            except ValueError:
                category_discount_id = None
        for item_id, item_data in self.__cart.items():
            if item_data.get("category_id") == category_id:
                item_data["category_discount_id"] = category_discount_id

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_sales_view(self) -> OrderViewResponseSchema:
        return await self.__order_view_service.get_view(Endpoint.ORDER_VIEW_SALES, None, None, None, self._module_id)

    def __build_image_maps(
        self, items: list[OrderViewSourceItemSchema]
    ) -> tuple[dict[int, str | None], dict[int, list[str]]]:
        api_url = self._settings.API_URL
        if self._settings.CLIENT == "web" and self._settings.PUBLIC_API_URL:
            api_url = self._settings.PUBLIC_API_URL
        image_map: dict[int, str | None] = {}
        images_map: dict[int, list[str]] = {}
        for item in items:
            url = None
            urls: list[str] = []
            for image in item.images:
                if image.url:
                    resolved_url = normalize_media_url(image.url, api_url)
                    urls.append(resolved_url or image.url)
                if image.is_primary:
                    url = normalize_media_url(image.url, api_url)
            if url is None and item.images:
                url = normalize_media_url(item.images[0].url, api_url)
            image_map[item.id] = url
            images_map[item.id] = urls
        return image_map, images_map
