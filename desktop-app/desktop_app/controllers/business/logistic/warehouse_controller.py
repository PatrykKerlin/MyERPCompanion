from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from services.business.logistic import WarehouseService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.warehouse_view import WarehouseView
from events.events import ViewRequested


class WarehouseController(
    BaseViewController[WarehouseService, WarehouseView, WarehousePlainSchema, WarehouseStrictSchema]
):
    _plain_schema_cls = WarehousePlainSchema
    _strict_schema_cls = WarehouseStrictSchema
    _service_cls = WarehouseService
    _view_cls = WarehouseView
    _endpoint = Endpoint.WAREHOUSES
    _view_key = View.WAREHOUSES

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        await self._handle_view_requested(event)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> WarehouseView:
        return WarehouseView(self, translation, mode, event.view_key, event.data)
