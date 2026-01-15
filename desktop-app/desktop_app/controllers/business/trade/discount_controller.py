from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from services.business.trade import DiscountService
from utils.enums import Endpoint, View, ViewMode
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

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> DiscountView:
        return DiscountView(self, translation, mode, event.view_key, event.data)
