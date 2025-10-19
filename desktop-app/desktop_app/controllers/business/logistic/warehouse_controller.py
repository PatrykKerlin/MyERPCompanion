from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.warehouse_schema import WarehousePlainSchema, WarehouseStrictSchema
from services.business.logistic import WarehouseService
from utils.enums import Endpoint, View, ViewMode
from views.business.logistic.warehouse_view import WarehouseView
from events.events import ViewRequested, ViewReady


class WarehouseController(
    BaseViewController[WarehouseService, WarehouseView, WarehousePlainSchema, WarehouseStrictSchema]
):
    _input_schema_cls = WarehousePlainSchema
    _output_schema_cls = WarehouseStrictSchema
    _service_cls = WarehouseService
    _view_cls = WarehouseView
    _endpoint = Endpoint.WAREHOUSES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key != View.WAREHOUSES:
            return
        self._open_loading_dialog()
        translation_service = self._state_store.app_state.translation
        self._key = event.key
        if event.data:
            mode = ViewMode.READ
            self._request_data.input_values = event.data
        else:
            mode = ViewMode.SEARCH
        self._view = WarehouseView(self, translation_service.items, mode, event.key, event.data)
        await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()
