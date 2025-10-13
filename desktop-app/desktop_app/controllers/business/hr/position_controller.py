from __future__ import annotations

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business import PositionPlainSchema, PositionStrictSchema
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.business.hr.position_service import PositionService
from utils.enums import View, ViewMode
from views.business.hr.position_view import PositionView
from events.events import ViewRequested, ViewReady


class PositionController(BaseViewController[PositionService, PositionView, PositionPlainSchema, PositionStrictSchema]):
    _input_schema_cls = PositionPlainSchema
    _output_schema_cls = PositionStrictSchema
    _service_cls = PositionService
    _view_cls = PositionView

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        self._open_loading_dialog()
        if event.key == View.POSITIONS:
            translation_service = self._state_store.app_state.translation
            self._key = event.key
            if event.data:
                mode = ViewMode.READ
                self._request_data.input_values = event.data
            else:
                mode = ViewMode.SEARCH
            currencies = await self.__get_all_currencies()
            departments = await self.__get_all_departments()
            self._view = PositionView(
                self, translation_service.items, mode, event.key, event.data, currencies, departments
            )
            await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
            self._close_loading_dialog()

    async def _perform_get_all(self) -> PaginatedResponseSchema[PositionPlainSchema]:
        filters: dict[str, str] = {}
        for field in self._request_data.selected_inputs:
            filters[field] = self._request_data.input_values.get(field, "").strip()
        params = {
            "page": self._request_data.page,
            "page_size": self._request_data.page_size,
            "sort_by": self._request_data.sort_by,
            "order": self._request_data.order,
            **filters,
        }
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.get_all,
            query_or_body_params=params,
            view_key=self._key,
        )

    async def _perform_get_one(self, id: int) -> PositionPlainSchema:
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.get_one,
            path_param=id,
            view_key=self._key,
        )

    async def _perform_create(self) -> PositionPlainSchema:
        data = PositionStrictSchema(**self._request_data.input_values)
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.create,
            query_or_body_params=data.model_dump(),
            view_key=self._key,
        )

    async def _perform_update(self, id: int) -> PositionPlainSchema:
        data = PositionStrictSchema(**self._request_data.input_values)
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.update,
            path_param=id,
            query_or_body_params=data.model_dump(),
            view_key=self._key,
        )

    async def _perform_delete(self, id: int) -> bool:
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.delete,
            path_param=id,
            view_key=self._key,
        )

    async def __get_all_currencies(self) -> dict[str, int]:
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.get_all_currencies,
            view_key=self._key,
        )

    async def __get_all_departments(self) -> dict[str, int]:
        return await self._call_api_with_token_refresh(
            service=self._service,
            func=self._service.get_all_departments,
            view_key=self._key,
        )
