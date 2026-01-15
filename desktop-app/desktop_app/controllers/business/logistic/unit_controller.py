from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.unit_schema import UnitPlainSchema, UnitStrictSchema
from services.business.logistic import UnitService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.unit_view import UnitView
from events.events import ViewRequested


class UnitController(BaseViewController[UnitService, UnitView, UnitPlainSchema, UnitStrictSchema]):
    _plain_schema_cls = UnitPlainSchema
    _strict_schema_cls = UnitStrictSchema
    _service_cls = UnitService
    _view_cls = UnitView
    _endpoint = Endpoint.UNITS
    _view_key = View.UNITS

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UnitView:
        return UnitView(self, translation, mode, event.view_key, event.data)
