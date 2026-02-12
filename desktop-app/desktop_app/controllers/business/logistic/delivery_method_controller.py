import asyncio

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from services.business.logistic import CarrierService, DeliveryMethodService, UnitService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.delivery_method_view import DeliveryMethodView


class DeliveryMethodController(
    BaseViewController[DeliveryMethodService, DeliveryMethodView, DeliveryMethodPlainSchema, DeliveryMethodStrictSchema]
):
    _plain_schema_cls = DeliveryMethodPlainSchema
    _strict_schema_cls = DeliveryMethodStrictSchema
    _service_cls = DeliveryMethodService
    _view_cls = DeliveryMethodView
    _endpoint = Endpoint.DELIVERY_METHODS
    _view_key = View.DELIVERY_METHODS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__carrier_service = CarrierService(self._settings, self._logger, self._tokens_accessor)
        self.__unit_service = UnitService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> DeliveryMethodView:
        carriers, units = await asyncio.gather(
            self.__perform_get_all_carriers(),
            self.__perform_get_all_units(),
        )
        carrier_id = None
        if event.data:
            carrier_id = event.data["carrier_id"]
            carriers = [item for item in carriers if item[0] == carrier_id]
        return DeliveryMethodView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            carriers,
            units,
            event.caller_view_key,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_carriers(self) -> list[tuple[int, str]]:
        schemas = await self.__carrier_service.get_all(Endpoint.CARRIERS, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_units(self) -> list[tuple[int, str]]:
        schemas = await self.__unit_service.get_all(Endpoint.UNITS, None, None, None, self._module_id)
        return [(schema.id, schema.name) for schema in schemas]
