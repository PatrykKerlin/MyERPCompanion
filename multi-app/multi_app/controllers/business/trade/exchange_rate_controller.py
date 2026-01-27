from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.exchange_rate_schema import ExchangeRatePlainSchema, ExchangeRateStrictSchema
from services.business.trade import CurrencyService, ExchangeRateService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.exchange_rate_view import ExchangeRateView
from events.events import ViewRequested
from config.context import Context


class ExchangeRateController(
    BaseViewController[ExchangeRateService, ExchangeRateView, ExchangeRatePlainSchema, ExchangeRateStrictSchema]
):
    _plain_schema_cls = ExchangeRatePlainSchema
    _strict_schema_cls = ExchangeRateStrictSchema
    _service_cls = ExchangeRateService
    _view_cls = ExchangeRateView
    _endpoint = Endpoint.EXCHANGE_RATES
    _view_key = View.EXCHANGE_RATES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ExchangeRateView:
        currencies = await self.__perform_get_all_currencies()
        return ExchangeRateView(self, translation, mode, event.view_key, event.data, currencies)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]
