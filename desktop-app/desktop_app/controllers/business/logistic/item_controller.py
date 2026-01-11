from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from services.business.logistic import CategoryService, ItemService, UnitService
from services.business.trade import CurrencyService, SupplierService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.item_view import ItemView
from events.events import ViewRequested


class ItemController(BaseViewController[ItemService, ItemView, ItemPlainSchema, ItemStrictSchema]):
    _plain_schema_cls = ItemPlainSchema
    _strict_schema_cls = ItemStrictSchema
    _service_cls = ItemService
    _view_cls = ItemView
    _endpoint = Endpoint.ITEMS
    _view_key = View.ITEMS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__category_service = CategoryService(self._settings, self._logger, self._tokens_accessor)
        self.__unit_service = UnitService(self._settings, self._logger, self._tokens_accessor)
        self.__supplier_service = SupplierService(self._settings, self._logger, self._tokens_accessor)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ItemView:
        categories = await self.__perform_get_all_categories()
        units = await self.__perform_get_all_units()
        suppliers = await self.__perform_get_all_suppliers()
        currencies = await self.__perform_get_all_currencies()
        return ItemView(self, translation, mode, event.view_key, event.data, categories, units, suppliers, currencies)

    async def __perform_get_all_categories(self) -> list[tuple[int, str]]:
        schemas = await self.__category_service.call_api_with_token_refresh(
            func=self.__category_service.get_all,
            endpoint=Endpoint.CATEGORIES,
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

    async def __perform_get_all_suppliers(self) -> list[tuple[int, str]]:
        schemas = await self.__supplier_service.call_api_with_token_refresh(
            func=self.__supplier_service.get_all,
            endpoint=Endpoint.SUPPLIERS,
            module_id=self._module_id,
        )
        return [(schema.id, schema.name) for schema in schemas]

    async def __perform_get_all_currencies(self) -> list[tuple[int, str]]:
        schemas = await self.__currency_service.call_api_with_token_refresh(
            func=self.__currency_service.get_all,
            endpoint=Endpoint.CURRENCIES,
            module_id=self._module_id,
        )
        return [(schema.id, schema.code) for schema in schemas]
