from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from services.business.hr import DepartmentService, PositionService
from services.business.trade import CurrencyService
from utils.enums import Endpoint, View, ViewMode
from views.business.hr.position_view import PositionView
from events.events import ViewRequested, ViewReady


class PositionController(BaseViewController[PositionService, PositionView, PositionPlainSchema, PositionStrictSchema]):
    _input_schema_cls = PositionPlainSchema
    _output_schema_cls = PositionStrictSchema
    _service_cls = PositionService
    _view_cls = PositionView
    _endpoint = Endpoint.POSITIONS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key != View.POSITIONS:
            return
        self._open_loading_dialog()
        translation_service = self._state_store.app_state.translation
        self._key = event.key
        if event.data:
            mode = ViewMode.READ
            self._request_data.input_values = event.data
        else:
            mode = ViewMode.SEARCH
        currencies = await self.__perform_get_all_currencies()
        departments = await self.__perform_get_all_departments()
        self._view = PositionView(self, translation_service.items, mode, event.key, event.data, currencies, departments)
        await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.call_api_with_token_refresh(
            func=self.__currency_service.get_all,
            endpoint=Endpoint.CURRENCIES,
            view_key=self._key,
        )

        return [(schema.id, schema.code) for schema in schemas]

    async def __perform_get_all_departments(self) -> list[tuple[int, str]]:
        schemas = await self.__department_service.call_api_with_token_refresh(
            func=self.__department_service.get_all,
            endpoint=Endpoint.DEPARTMENTS,
            view_key=self._key,
        )

        return [(schema.id, schema.code) for schema in schemas]
