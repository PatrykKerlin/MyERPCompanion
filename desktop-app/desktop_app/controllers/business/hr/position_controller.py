from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.hr.position_schema import PositionPlainSchema, PositionStrictSchema
from services.business.hr import DepartmentService, PositionService
from services.business.trade import CurrencyService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.hr.position_view import PositionView
from events.events import ViewRequested


class PositionController(BaseViewController[PositionService, PositionView, PositionPlainSchema, PositionStrictSchema]):
    _plain_schema_cls = PositionPlainSchema
    _strict_schema_cls = PositionStrictSchema
    _service_cls = PositionService
    _view_cls = PositionView
    _endpoint = Endpoint.POSITIONS
    _view_key = View.POSITIONS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PositionView:
        currencies = await self.__perform_get_all_currencies()
        departments = await self.__perform_get_all_departments()
        return PositionView(self, translation, mode, event.view_key, event.data, currencies, departments)

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]

    async def __perform_get_all_departments(self) -> list[tuple[int, str]]:
        schemas = await self.__department_service.get_all(Endpoint.DEPARTMENTS, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]
