from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema
from services.business.logistic import CarrierService, DeliveryMethodService
from services.business.trade import CurrencyService
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

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__delivery_method_service = DeliveryMethodService(self._settings, self._logger, self._tokens_accessor)

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        await self._handle_view_requested(event)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CarrierView:
        currencies = await self.__perform_get_all_currencies()
        if event.data:
            delivery_method_schemas = await self.__perform_get_delivery_methods_for_id(event.data["id"])
            delivery_methods = [schema.model_dump() for schema in delivery_method_schemas]
        else:
            delivery_methods = [{}]
        return CarrierView(self, translation, mode, event.view_key, event.data, currencies, delivery_methods)

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.call_api_with_token_refresh(
            func=self.__currency_service.get_all,
            endpoint=Endpoint.CURRENCIES,
            module_id=self._module_id,
        )

        return [(schema.id, schema.code) for schema in schemas]

    async def __perform_get_delivery_methods_for_id(self, id: int) -> list[DeliveryMethodPlainSchema]:
        return await self.__delivery_method_service.call_api_with_token_refresh(
            func=self.__delivery_method_service.get_all,
            endpoint=Endpoint.DELIVERY_METHODS,
            query_params={"carrier_id": id},
            module_id=self._module_id,
        )
