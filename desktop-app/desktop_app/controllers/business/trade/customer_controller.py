import asyncio
from typing import Any

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from controllers.mixins.user_link_controller_mixin import UserLinkControllerMixin
from events.events import ViewRequested
from schemas.business.trade.assoc_customer_discount_schema import (
    AssocCustomerDiscountPlainSchema,
    AssocCustomerDiscountStrictSchema,
)
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.trade import AssocCustomerDiscountService, CustomerService, DiscountService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.trade.customer_view import CustomerView


DiscountTransferItem = tuple[int, str, str, float | None]


class CustomerController(
    UserLinkControllerMixin,
    BaseViewController[CustomerService, CustomerView, CustomerPlainSchema, CustomerStrictSchema],
):
    _plain_schema_cls = CustomerPlainSchema
    _strict_schema_cls = CustomerStrictSchema
    _service_cls = CustomerService
    _view_cls = CustomerView
    _endpoint = Endpoint.CUSTOMERS
    _view_key = View.CUSTOMERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._init_user_link_mixin()
        self.__discount_service = DiscountService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_customer_discount_service = AssocCustomerDiscountService(
            self._settings, self._logger, self._tokens_accessor
        )

    def on_discount_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view:
            return
        self._page.run_task(self.__handle_discount_save)

    def on_discount_delete_clicked(self, discount_ids: list[int]) -> None:
        if not self._view or not discount_ids:
            return
        self._page.run_task(self.__handle_discount_delete, discount_ids)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CustomerView:
        discount_source_items: list[DiscountTransferItem] = []
        discount_target_items: list[DiscountTransferItem] = []
        user_options: list[tuple[int, str]] = []
        if mode != ViewMode.SEARCH:
            discounts = await self.__perform_get_all_customer_discounts()
            target_ids = set(self.__extract_discount_ids(event.data))
            discount_target_items = [
                (discount.id, discount.code, discount.name, discount.percent)
                for discount in discounts
                if discount.id in target_ids
            ]
            discount_source_items = [
                (discount.id, discount.code, discount.name, discount.percent)
                for discount in discounts
                if discount.id not in target_ids
            ]
        if mode == ViewMode.SEARCH:
            users, customers = await asyncio.gather(
                self._perform_get_all_users(),
                self._perform_get_all_customers(),
            )
            user_options = self._get_user_link_options(mode, event, users, [], customers)
        else:
            users, customers = await asyncio.gather(
                self._perform_get_all_users(),
                self._perform_get_all_customers(),
            )
            user_options = self._get_user_link_options(mode, event, users, [], customers)
        return CustomerView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            discount_source_items,
            discount_target_items,
            user_options,
            self.on_discount_save_clicked,
            self.on_discount_delete_clicked,
        )

    @property
    def _user_link_view_key(self) -> View:
        return View.CUSTOMERS

    @property
    def _user_link_entity_key(self) -> str:
        return "customer_id"

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

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_customer_discounts(self) -> list[DiscountPlainSchema]:
        discounts = await self.__discount_service.get_all(Endpoint.DISCOUNTS, None, None, None, self._module_id)
        return [discount for discount in discounts if discount.for_customers]

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

    @staticmethod
    def __extract_discount_ids(data: dict[str, Any] | None) -> list[int]:
        if not data:
            return []
        raw_ids = data.get("discount_ids")
        if isinstance(raw_ids, list):
            return [item for item in raw_ids if isinstance(item, int)]
        raw_discounts = data.get("discounts")
        if isinstance(raw_discounts, list):
            ids: list[int] = []
            for raw in raw_discounts:
                if isinstance(raw, dict) and isinstance(raw.get("id"), int):
                    ids.append(raw["id"])
            return ids
        return []

    async def __refresh_customer_discount_lists(self, customer_id: int) -> None:
        if not self._view:
            return
        customer = await self.__perform_get_customer(customer_id)
        if not customer:
            return
        data_row = customer.model_dump()
        discounts = await self.__perform_get_all_customer_discounts()
        target_ids = set(self.__extract_discount_ids(data_row))
        target_items = [
            (discount.id, discount.code, discount.name, discount.percent)
            for discount in discounts
            if discount.id in target_ids
        ]
        source_items = [
            (discount.id, discount.code, discount.name, discount.percent)
            for discount in discounts
            if discount.id not in target_ids
        ]
        self._view.set_discount_target_items(target_items)
        self._view.set_discount_source_items(source_items)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_customer(self, customer_id: int) -> CustomerPlainSchema | None:
        return await self._service.get_one(Endpoint.CUSTOMERS, customer_id, None, None, self._module_id)
