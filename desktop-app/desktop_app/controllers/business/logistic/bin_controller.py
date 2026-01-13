from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from services.business.logistic import BinService, WarehouseService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.bin_view import BinView
from events.events import ViewRequested


class BinController(BaseViewController[BinService, BinView, BinPlainSchema, BinStrictSchema]):
    _plain_schema_cls = BinPlainSchema
    _strict_schema_cls = BinStrictSchema
    _service_cls = BinService
    _view_cls = BinView
    _endpoint = Endpoint.BINS
    _view_key = View.BINS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__warehouse_service = WarehouseService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinView:
        warehouses = await self.__perform_get_all_warehouses()
        return BinView(self, translation, mode, event.view_key, event.data, warehouses)

    async def __perform_get_all_warehouses(self) -> list[tuple[int, str]]:
        schemas = await self.__warehouse_service.call_api_with_token_refresh(
            func=self.__warehouse_service.get_all,
            endpoint=Endpoint.WAREHOUSES,
            module_id=self._module_id,
        )

        return [(schema.id, schema.name) for schema in schemas]

    # async def __perform_get_items_for_id(self, id: int) -> list[ItemPlainSchema]:
    #     return await self.__delivery_method_service.call_api_with_token_refresh(
    #         func=self.__delivery_method_service.get_all,
    #         endpoint=Endpoint.DELIVERY_METHODS,
    #         query_params={"carrier_id": id},
    #         module_id=self._module_id,
    #     )
