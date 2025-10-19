from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from services.business.logistic import BinService, WarehouseService
from utils.enums import Endpoint, View, ViewMode
from views.business.logistic.bin_view import BinView
from events.events import ViewRequested, ViewReady


class BinController(BaseViewController[BinService, BinView, BinPlainSchema, BinStrictSchema]):
    _input_schema_cls = BinPlainSchema
    _output_schema_cls = BinStrictSchema
    _service_cls = BinService
    _view_cls = BinView
    _endpoint = Endpoint.BINS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__warehouse_service = WarehouseService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key != View.BINS:
            return
        self._open_loading_dialog()
        translation_service = self._state_store.app_state.translation
        self._key = event.key
        if event.data:
            mode = ViewMode.READ
            self._request_data.input_values = event.data
        else:
            mode = ViewMode.SEARCH
        warehouses = await self.__perform_get_all_warehouses()
        self._view = BinView(self, translation_service.items, mode, event.key, event.data, warehouses)
        await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()

    async def __perform_get_all_warehouses(self) -> list[tuple[int, str]]:
        schemas = await self.__warehouse_service.call_api_with_token_refresh(
            func=self.__warehouse_service.get_all,
            endpoint=Endpoint.WAREHOUSES,
            view_key=self._key,
        )

        return [(schema.id, schema.name) for schema in schemas]
