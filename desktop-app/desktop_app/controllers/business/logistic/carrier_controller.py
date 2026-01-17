from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.carrier_schema import CarrierPlainSchema, CarrierStrictSchema
from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema
from services.business.logistic import CarrierService, DeliveryMethodService
from services.business.trade import CurrencyService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.carrier_view import CarrierView
from events.events import ViewRequested

import flet as ft


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

    def on_table_row_clicked(self, result_id: int) -> None:
        self._page.run_task(
            self._execute_row_clicked,
            result_id,
            View.DELIVERY_METHODS,
            self.__delivery_method_service,
            Endpoint.DELIVERY_METHODS,
        )

    def on_add_delivery_method_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        self._page.run_task(self.__open_delivery_method_create_dialog)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CarrierView:
        currencies = await self.__perform_get_all_currencies()
        if event.data:
            delivery_method_schemas = await self.__perform_get_delivery_methods_for_id(event.data["id"])
            delivery_methods = [schema.model_dump() for schema in delivery_method_schemas]
        else:
            delivery_methods = []
        return CarrierView(self, translation, mode, event.view_key, event.data, currencies, delivery_methods)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.get_all(Endpoint.CURRENCIES, None, None, None, self._module_id)
        return [(schema.id, schema.code) for schema in schemas]

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_delivery_methods_for_id(self, id: int) -> list[DeliveryMethodPlainSchema]:
        query_params = {"carrier_id": id}
        return await self.__delivery_method_service.get_all(
            Endpoint.DELIVERY_METHODS, None, query_params, None, self._module_id
        )

    async def __open_delivery_method_create_dialog(self) -> None:
        if not self._view or not self._view.data_row:
            return
        id_value = self._view.data_row["id"]
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=self._module_id,
                view_key=View.DELIVERY_METHODS,
                data={"carrier_id": id_value},
                is_dialog=True,
                caller_view_key=self._view_key,
            ),
        )
