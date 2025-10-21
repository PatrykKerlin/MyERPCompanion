from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from services.business.logistic import CarrierService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.carrier_view import CarrierView
from events.events import ViewRequested


class CarrierController(BaseViewController[CarrierService, CarrierView, CarrierPlainSchema, CarrierStrictSchema]):
    _plain_schema_cls = CarrierPlainSchema
    _strict_schema_cls = CarrierStrictSchema
    _service_cls = CarrierService
    _view_cls = CarrierView
    _endpoint = Endpoint.CARRIERS
    _view_key = View.CARRIERS

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        await self._handle_view_requested(event)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CarrierView:
        return CarrierView(self, translation, mode, event.view_key, event.data)
