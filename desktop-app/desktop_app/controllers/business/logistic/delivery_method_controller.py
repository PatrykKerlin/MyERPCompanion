from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema, DeliveryMethodStrictSchema
from services.business.logistic import CarrierService, DeliveryMethodService, UnitService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.delivery_method_view import DeliveryMethodView
from events.events import ViewRequested


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
        carriers = await self.__perform_get_all_carriers()
        units = await self.__perform_get_all_units()
        return DeliveryMethodView(
            self, translation, mode, event.view_key, event.data, event.is_dialog, event.caller_view_key, carriers, units
        )

    async def __perform_get_all_carriers(self) -> list[tuple[int, str]]:
        schemas = await self.__carrier_service.call_api_with_token_refresh(
            func=self.__carrier_service.get_all,
            endpoint=Endpoint.CARRIERS,
            module_id=self._module_id,
        )

        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_units(self) -> list[tuple[int, str]]:
        schemas = await self.__unit_service.call_api_with_token_refresh(
            func=self.__unit_service.get_all,
            endpoint=Endpoint.UNITS,
            module_id=self._module_id,
        )

        return [(schema.id, schema.name) for schema in schemas]
