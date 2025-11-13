from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.business.logistic import ItemService
from services.core.image_service import ImageService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.item_view import ItemView
from events.events import ViewRequested


class ItemController(BaseViewController[ItemService, ItemView, ItemPlainSchema, ItemStrictSchema]):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = ItemView
    _endpoint = Endpoint.ITEMS
    _view_key = View.ITEMS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__image_service = ImageService(self._settings, self._logger, self._tokens_accessor)

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        await self._handle_view_requested(event)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemView:
        return ItemView(self, translation, mode, event.view_key, event.data)
