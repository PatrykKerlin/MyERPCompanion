from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema

from services.business.trade import CurrencyService, SupplierService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.supplier_view import SupplierView
from events.events import ViewRequested


class SupplierController(BaseViewController[SupplierService, SupplierView, SupplierPlainSchema, SupplierStrictSchema]):
    _plain_schema_cls = SupplierPlainSchema
    _strict_schema_cls = SupplierStrictSchema
    _service_cls = SupplierService
    _view_cls = SupplierView
    _endpoint = Endpoint.SUPPLIERS
    _view_key = View.SUPPLIERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> SupplierView:
        currencies = await self.__perform_get_all_currencies()
        return SupplierView(self, translation, mode, event.view_key, event.data, currencies)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]
