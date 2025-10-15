from __future__ import annotations

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business import DepartmentPlainSchema, DepartmentStrictSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.business.hr.department_service import DepartmentService
from utils.enums import Endpoint, View, ViewMode
from views.business.hr.department_view import DepartmentView
from events.events import ViewRequested, ViewReady


class DepartmentController(
    BaseViewController[DepartmentService, DepartmentView, DepartmentPlainSchema, DepartmentStrictSchema]
):
    _input_schema_cls = DepartmentPlainSchema
    _output_schema_cls = DepartmentStrictSchema
    _service_cls = DepartmentService
    _view_cls = DepartmentView

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key == View.DEPARTMENTS:
            translation_service = self._state_store.app_state.translation
            self._key = event.key
            if event.data:
                mode = ViewMode.READ
                self._request_data.input_values = event.data
            else:
                mode = ViewMode.SEARCH
            self._view = DepartmentView(self, translation_service.items, mode, event.key, event.data)
            await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))

    async def _perform_get_page(self) -> PaginatedResponseSchema[DepartmentPlainSchema]:
        filters: dict[str, str] = {}
        for field in self._request_data.selected_inputs:
            filters[field] = self._request_data.input_values.get(field, "")
        params = {
            "page": self._request_data.page,
            "page_size": self._request_data.page_size,
            "sort_by": self._request_data.sort_by,
            "order": self._request_data.order,
            **filters,
        }
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_page,
            endpoint=Endpoint.DEPARTMENTS,
            query_params=params,
            view_key=self._key,
        )

    async def _perform_get_one(self, id: int) -> DepartmentPlainSchema:
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_one,
            endpoint=Endpoint.DEPARTMENTS,
            path_param=id,
            view_key=self._key,
        )

    async def _perform_create(self) -> DepartmentPlainSchema:
        data = DepartmentStrictSchema(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.create,
            endpoint=Endpoint.DEPARTMENTS,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_update(self, id: int) -> DepartmentPlainSchema:
        data = DepartmentStrictSchema(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.update,
            endpoint=Endpoint.DEPARTMENTS,
            path_param=id,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_delete(self, id: int) -> bool:
        return await self._service.call_api_with_token_refresh(
            func=self._service.delete,
            endpoint=Endpoint.DEPARTMENTS,
            path_param=id,
            view_key=self._key,
        )
