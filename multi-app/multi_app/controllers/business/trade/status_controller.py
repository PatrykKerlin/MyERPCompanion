from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.status_schema import StatusPlainSchema, StatusStrictSchema
from services.business.trade import StatusService
from utils.enums import Endpoint, View, ViewMode
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

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> StatusView:
        return StatusView(self, translation, mode, event.view_key, event.data)

