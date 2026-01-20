from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.trade.assoc_customer_discount_schema import (
    AssocCustomerDiscountPlainSchema,
    AssocCustomerDiscountStrictSchema,
)
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.core.param_schema import IdsPayloadSchema

# from schemas.core.user_schema import UserPlainSchema
from services.business.trade import AssocCustomerDiscountService, CustomerService, DiscountService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.customer_view import CustomerView
from events.events import ViewRequested
import flet as ft


class CustomerController(BaseViewController[CustomerService, CustomerView, CustomerPlainSchema, CustomerStrictSchema]):
    _plain_schema_cls = CustomerPlainSchema
    _strict_schema_cls = CustomerStrictSchema
    _service_cls = CustomerService
    _view_cls = CustomerView
    _endpoint = Endpoint.CUSTOMERS
    _view_key = View.CUSTOMERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__discount_service = DiscountService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_customer_discount_service = AssocCustomerDiscountService(
            self._settings, self._logger, self._tokens_accessor
        )
        # self.__user_service = UserService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CustomerView:
        # users = self.__perform_get_all_users()
        discount_source_items: list[tuple[int, str]] = []
        discount_target_items: list[tuple[int, str]] = []
        if mode != ViewMode.SEARCH:
            discount_target_items = self.__extract_customer_discounts(event.data)
            target_ids = {item_id for item_id, _ in discount_target_items}
            discount_source_items = await self.__perform_get_customer_discount_options(target_ids)
        return CustomerView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            discount_source_items,
            discount_target_items,
            self.on_discount_save_clicked,
            self.on_discount_delete_clicked,
        )

    def on_discount_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_discount_save)

    def on_discount_delete_clicked(self, discount_ids: list[int]) -> None:
        if not self._view or not discount_ids:
            return
        self._page.run_task(self.__handle_discount_delete, discount_ids)

    async def __handle_discount_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        customer_id = self._view.data_row["id"]
        pending_ids = self._view.get_pending_discount_ids()
        if not pending_ids:
            return
        payload = [
            AssocCustomerDiscountStrictSchema(customer_id=customer_id, discount_id=discount_id)
            for discount_id in pending_ids
        ]
        await self.__perform_create_customer_discounts(payload)
        await self.__refresh_customer_discount_lists(customer_id)

    async def __handle_discount_delete(self, discount_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        customer_id = self._view.data_row["id"]
        await self.__perform_delete_customer_discounts(customer_id, discount_ids)
        await self.__refresh_customer_discount_lists(customer_id)

    # async def __perform_get_all_users(self) -> list[UserPlainSchema]:
    #     return await self.__user_service.call_api_with_token_refresh(
    #         func=self.__user_service.get_all,
    #         endpoint=Endpoint.USERS,
    #         module_id=self._module_id,
    #     )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customer_discount_options(self, exclude_ids: set[int]) -> list[tuple[int, str]]:
        discounts = await self.__discount_service.get_all(Endpoint.DISCOUNTS, None, None, None, self._module_id)
        options: list[tuple[int, str]] = []
        for discount in discounts:
            if not discount.for_customers:
                continue
            if discount.id in exclude_ids:
                continue
            options.append((discount.id, discount.code))
        return options

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_customer_discounts(self, payload: list[AssocCustomerDiscountStrictSchema]) -> None:
        await self._perform_create_bulk(
            self.__assoc_customer_discount_service, Endpoint.CUSTOMER_DISCOUNTS_CREATE_BULK, payload
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_customer_discounts(self, customer_id: int, discount_ids: list[int]) -> None:
        assoc_rows: list[AssocCustomerDiscountPlainSchema] = await self.__assoc_customer_discount_service.get_all(
            Endpoint.CUSTOMER_DISCOUNTS, None, {"customer_id": customer_id}, None, self._module_id
        )
        assoc_ids = [row.id for row in assoc_rows if row.discount_id in discount_ids]
        if not assoc_ids:
            return
        body_params = IdsPayloadSchema(ids=assoc_ids)
        await self.__assoc_customer_discount_service.delete_bulk(
            Endpoint.CUSTOMER_DISCOUNTS_DELETE_BULK, None, None, body_params, self._module_id
        )

    def __extract_customer_discounts(self, data: dict[str, Any] | None) -> list[tuple[int, str]]:
        if not data:
            return []
        raw_items = data["discounts"]
        items: list[tuple[int, str]] = []
        for raw in raw_items:
            items.append((raw["id"], raw["code"]))
        return items

    async def __refresh_customer_discount_lists(self, customer_id: int) -> None:
        if not self._view:
            return
        customer = await self.__perform_get_customer(customer_id)
        if not customer:
            return
        target_items = [(discount.id, discount.code) for discount in customer.discounts]
        target_ids = {item_id for item_id, _ in target_items}
        source_items = await self.__perform_get_customer_discount_options(target_ids)
        self._view.set_discount_target_items(target_items)
        self._view.set_discount_source_items(source_items)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customer(self, customer_id: int) -> CustomerPlainSchema | None:
        return await self._service.get_one(Endpoint.CUSTOMERS, customer_id, None, None, self._module_id)
