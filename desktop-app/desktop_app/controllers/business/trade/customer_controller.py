from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema

# from schemas.core.user_schema import UserPlainSchema
from services.business.trade import CustomerService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.customer_view import CustomerView
from events.events import ViewRequested


class CustomerController(BaseViewController[CustomerService, CustomerView, CustomerPlainSchema, CustomerStrictSchema]):
    _plain_schema_cls = CustomerPlainSchema
    _strict_schema_cls = CustomerStrictSchema
    _service_cls = CustomerService
    _view_cls = CustomerView
    _endpoint = Endpoint.CUSTOMERS
    _view_key = View.CUSTOMERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        # self.__user_service = UserService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CustomerView:
        # users = self.__perform_get_all_users()
        return CustomerView(self, translation, mode, event.view_key, event.data)

    # async def __perform_get_all_users(self) -> list[UserPlainSchema]:
    #     return await self.__user_service.call_api_with_token_refresh(
    #         func=self.__user_service.get_all,
    #         endpoint=Endpoint.USERS,
    #         module_id=self._module_id,
    #     )
