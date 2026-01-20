import asyncio
from typing import Any
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.status_schema import StatusPlainSchema, StatusStrictSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.trade import StatusService, OrderService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.status_view import StatusView
from events.events import ViewRequested


class StatusController(BaseViewController[StatusService, StatusView, StatusPlainSchema, StatusStrictSchema]):
    _plain_schema_cls = StatusPlainSchema
    _strict_schema_cls = StatusStrictSchema
    _service_cls = StatusService
    _view_cls = StatusView
    _endpoint = Endpoint.STATUSES
    _view_key = View.STATUSES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)

    def on_table_row_clicked(self, result_id: int) -> None:
        if not self._view or not self._view.data_row:
            return
        if self._view.data_row.get("supplier_id"):
            view = View.PURCHASE_ORDERS
        else:
            view = View.SALES_ORDERS
        self._page.run_task(
            self._execute_row_clicked,
            result_id,
            view,
            self.__order_service,
            Endpoint.ORDERS,
        )

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> StatusView:
        if event.data:
            orders = await self.__perform_get_orders_for_ids(event.data["order_ids"])
        else:
            orders = []
        return StatusView(self, translation, mode, event.view_key, event.data, orders)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_orders_for_ids(self, order_ids: list[int]) -> list[dict[str, Any]]:
        body_params = IdsPayloadSchema(ids=order_ids)
        order_schemas = await self.__order_service.get_bulk(
            Endpoint.ORDERS_GET_BULK, None, None, body_params, self._module_id
        )
        orders: list[dict[str, Any]] = []
        for order_schema in order_schemas:
            order = order_schema.model_dump()
            orders.append(order)
        return orders
