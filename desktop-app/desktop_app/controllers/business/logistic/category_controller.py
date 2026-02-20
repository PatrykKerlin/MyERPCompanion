from typing import Any

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.business.logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
from schemas.business.trade.assoc_category_discount_schema import (
    AssocCategoryDiscountPlainSchema,
    AssocCategoryDiscountStrictSchema,
)
from schemas.business.trade.discount_schema import DiscountPlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from services.business.logistic import CategoryService
from services.business.trade import AssocCategoryDiscountService, DiscountService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.category_view import CategoryView

DiscountTransferItem = tuple[int, str, str, float | None]


class CategoryController(BaseViewController[CategoryService, CategoryView, CategoryPlainSchema, CategoryStrictSchema]):
    _plain_schema_cls = CategoryPlainSchema
    _strict_schema_cls = CategoryStrictSchema
    _service_cls = CategoryService
    _view_cls = CategoryView
    _endpoint = Endpoint.CATEGORIES
    _view_key = View.CATEGORIES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__discount_service = DiscountService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_category_discount_service = AssocCategoryDiscountService(
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

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CategoryView:
        discount_source_items: list[DiscountTransferItem] = []
        discount_target_items: list[DiscountTransferItem] = []
        if mode != ViewMode.SEARCH:
            discount_target_items = await self.__extract_category_discounts(event.data)
            target_ids = {item[0] for item in discount_target_items}
            discount_source_items = await self.__perform_get_category_discount_options(target_ids)
        return CategoryView(
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

    async def __handle_discount_save(self) -> None:
        if not self._view or not self._view.data_row:
            return
        category_id = self._view.data_row["id"]
        pending_ids = self._view.get_pending_discount_ids()
        if not pending_ids:
            return
        payload = [
            AssocCategoryDiscountStrictSchema(category_id=category_id, discount_id=discount_id)
            for discount_id in pending_ids
        ]
        created = await self.__perform_create_category_discounts(payload)
        if not created:
            return
        await self.__refresh_category_discount_lists(category_id)

    async def __handle_discount_delete(self, discount_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        category_id = self._view.data_row["id"]
        deleted_count = await self.__perform_delete_category_discounts(category_id, discount_ids)
        if deleted_count is None:
            return
        await self.__refresh_category_discount_lists(category_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_category(self, category_id: int) -> CategoryPlainSchema | None:
        return await self._service.get_one(Endpoint.CATEGORIES, category_id, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_category_discount_options(self, exclude_ids: set[int]) -> list[DiscountTransferItem]:
        discounts = await self.__discount_service.get_all(Endpoint.DISCOUNTS, None, None, None, self._module_id)
        options: list[DiscountTransferItem] = []
        for discount in discounts:
            if not discount.for_categories:
                continue
            if discount.id in exclude_ids:
                continue
            options.append((discount.id, discount.code, discount.name, discount.percent))
        return options

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_category_discounts(self, category_id: int) -> list[AssocCategoryDiscountPlainSchema]:
        return await self.__assoc_category_discount_service.get_all(
            Endpoint.CATEGORY_DISCOUNTS, None, {"category_id": category_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_discounts_by_ids(self, discount_ids: list[int]) -> list[DiscountPlainSchema]:
        if not discount_ids:
            return []
        body_params = IdsPayloadSchema(ids=discount_ids)
        return await self.__discount_service.get_bulk(
            Endpoint.DISCOUNTS_GET_BULK, None, None, body_params, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_category_discounts(self, payload: list[AssocCategoryDiscountStrictSchema]) -> bool:
        await self._perform_create_bulk(
            self.__assoc_category_discount_service, Endpoint.CATEGORY_DISCOUNTS_CREATE_BULK, payload
        )
        return True

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_category_discounts(self, category_id: int, discount_ids: list[int]) -> int | None:
        assoc_rows = await self.__perform_get_category_discounts(category_id)
        assoc_ids = [row.id for row in assoc_rows if row.discount_id in discount_ids]
        if not assoc_ids:
            return 0
        body_params = IdsPayloadSchema(ids=assoc_ids)
        await self.__assoc_category_discount_service.delete_bulk(
            Endpoint.CATEGORY_DISCOUNTS_DELETE_BULK, None, None, body_params, self._module_id
        )
        return len(assoc_ids)

    async def __extract_category_discounts(self, data: dict[str, Any] | None) -> list[DiscountTransferItem]:
        discount_ids = self.__extract_discount_ids(data)
        if not discount_ids:
            return []
        discounts = await self.__perform_get_discounts_by_ids(discount_ids)
        return [(discount.id, discount.code, discount.name, discount.percent) for discount in discounts]

    @staticmethod
    def __extract_discount_ids(data: dict[str, Any] | None) -> list[int]:
        if not data:
            return []
        raw_ids = data.get("discount_ids")
        if not isinstance(raw_ids, list):
            return []
        return [item for item in raw_ids if isinstance(item, int)]

    async def __refresh_category_discount_lists(self, category_id: int) -> None:
        if not self._view:
            return
        category = await self.__perform_get_category(category_id)
        if not category:
            return
        discount_ids = self.__extract_discount_ids(category.model_dump())
        discounts = await self.__perform_get_discounts_by_ids(discount_ids)
        target_items = [(discount.id, discount.code, discount.name, discount.percent) for discount in discounts]
        target_ids = {item[0] for item in target_items}
        source_items = await self.__perform_get_category_discount_options(target_ids)
        self._view.set_discount_target_items(target_items)
        self._view.set_discount_source_items(source_items)
