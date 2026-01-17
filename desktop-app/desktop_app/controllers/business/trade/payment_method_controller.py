from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.payment_method_schema import PaymentMethodPlainSchema, PaymentMethodStrictSchema
from services.business.trade import PaymentMethodService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from events.events import ViewRequested
from views.business.trade.payment_method_view import PaymentMethodView


class PaymentMethodController(
    BaseViewController[PaymentMethodService, PaymentMethodView, PaymentMethodPlainSchema, PaymentMethodStrictSchema]
):
    _plain_schema_cls = PaymentMethodPlainSchema
    _strict_schema_cls = PaymentMethodStrictSchema
    _service_cls = PaymentMethodService
    _view_cls = PaymentMethodView
    _endpoint = Endpoint.PAYMENT_METHODS
    _view_key = View.PAYMENT_METHODS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PaymentMethodView:
        return PaymentMethodView(self, translation, mode, event.view_key, event.data)
