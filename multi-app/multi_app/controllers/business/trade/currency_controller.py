from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from services.business.trade import CurrencyService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.currency_view import CurrencyView
from events.events import ViewRequested


class CurrencyController(BaseViewController[CurrencyService, CurrencyView, CurrencyPlainSchema, CurrencyStrictSchema]):
    _plain_schema_cls = CurrencyPlainSchema
    _strict_schema_cls = CurrencyStrictSchema
    _service_cls = CurrencyService
    _view_cls = CurrencyView
    _endpoint = Endpoint.CURRENCIES
    _view_key = View.CURRENCIES

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CurrencyView:
        return CurrencyView(self, translation, mode, event.view_key, event.data)
