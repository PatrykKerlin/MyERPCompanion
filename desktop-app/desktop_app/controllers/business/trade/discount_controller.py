from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from services.business.trade import CurrencyService, DiscountService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.discount_view import DiscountView
from events.events import ViewRequested


class DiscountController(BaseViewController[DiscountService, DiscountView, DiscountPlainSchema, DiscountStrictSchema]):
    _plain_schema_cls = DiscountPlainSchema
    _strict_schema_cls = DiscountStrictSchema
    _service_cls = DiscountService
    _view_cls = DiscountView
    _endpoint = Endpoint.DISCOUNTS
    _view_key = View.DISCOUNTS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> DiscountView:
        currencies = await self.__perform_get_all_currencies()
        return DiscountView(self, translation, mode, event.view_key, event.data, currencies)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]
