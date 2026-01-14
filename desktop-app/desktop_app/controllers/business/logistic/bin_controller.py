from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.business.logistic.item_schema import ItemPlainSchema
from services.business.logistic import AssocBinItemService, BinService, WarehouseService
from services.business.logistic.item_service import ItemService
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
        self.__item_service = ItemService(self._settings, self._logger, self._tokens_accessor)
        self.__bin_item_service = AssocBinItemService(self._settings, self._logger, self._tokens_accessor)

    def on_table_row_clicked(self, result_id: int) -> None:
        self._page.run_task(
            self._execute_row_clicked,
            result_id,
            View.ITEMS,
            self.__item_service,
            Endpoint.ITEMS,
        )

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> BinView:
        warehouses = await self.__perform_get_all_warehouses()
        if event.data:
            item_schemas = await self.__perform_get_items_for_ids(event.data["item_ids"])
            bin_item_quantities = await self.__perform_get_bin_item_quantities(event.data["id"])
            items = []
            for item_schema in item_schemas:
                row = item_schema.model_dump()
                row["quantity"] = bin_item_quantities.get(item_schema.id, 0)
                items.append(row)
        else:
            items = []
        return BinView(self, translation, mode, event.view_key, event.data, warehouses, items)

    async def __perform_get_all_warehouses(self) -> list[tuple[int, str]]:
        schemas = await self.__warehouse_service.call_api_with_token_refresh(
            func=self.__warehouse_service.get_all,
            endpoint=Endpoint.WAREHOUSES,
            module_id=self._module_id,
        )

        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_items_for_ids(self, item_ids: list[int]) -> list[ItemPlainSchema]:
        return await self.__item_service.call_api_with_token_refresh(
            func=self.__item_service.get_bulk,
            endpoint=Endpoint.ITEMS_GET_BULK,
            body_params={"ids": item_ids},
            module_id=self._module_id,
        )

    async def __perform_get_bin_item_quantities(self, bin_id: int) -> dict[int, int]:
        bin_item_schemas = await self.__bin_item_service.call_api_with_token_refresh(
            func=self.__bin_item_service.get_all,
            endpoint=Endpoint.BIN_ITEMS,
            query_params={"bin_id": bin_id},
            module_id=self._module_id,
        )
        return {schema.item_id: schema.quantity for schema in bin_item_schemas}
