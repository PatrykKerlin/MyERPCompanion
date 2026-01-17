from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from services.business.trade import OrderService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from events.events import ViewRequested
from views.business.trade.purchase_order_view import PurchaseOrderView


class PurchaseOrderController(BaseViewController[OrderService, PurchaseOrderView, OrderPlainSchema, OrderStrictSchema]):
    _plain_schema_cls = OrderPlainSchema
    _strict_schema_cls = OrderStrictSchema
    _service_cls = OrderService
    _view_cls = PurchaseOrderView
    _endpoint = Endpoint.PURCHASE_ORDERS
    _view_key = View.PURCHASE_ORDERS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> PurchaseOrderView:
        return PurchaseOrderView(self, translation, mode, event.view_key, event.data)
