from __future__ import annotations

from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.web.orders_view import OrdersView

from config.context import Context


class OrdersService(BaseService[BasePlainSchema, BaseStrictSchema]):
    _plain_schema_cls = BasePlainSchema


class OrdersController(BaseViewController[OrdersService, OrdersView, BasePlainSchema, BaseStrictSchema]):
    _plain_schema_cls = BasePlainSchema
    _strict_schema_cls = BaseStrictSchema
    _service_cls = OrdersService
    _view_cls = OrdersView
    _endpoint = Endpoint.ORDERS
    _view_key = View.SALES_ORDERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> OrdersView:
        return OrdersView(controller=self, translation=translation)
