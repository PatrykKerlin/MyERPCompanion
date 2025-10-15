from __future__ import annotations

from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from services.business.hr.department_service import DepartmentService
from services.business.hr.employee_service import EmployeeService
from services.business.trade.currency_service import CurrencyService
from utils.enums import Endpoint, View, ViewMode
from views.business.hr.employee_view import EmployeeView
from events.events import ViewRequested, ViewReady


class EmployeeController(BaseViewController[EmployeeService, EmployeeView, EmployeePlainSchema, EmployeeStrictSchema]):
    _input_schema_cls = EmployeePlainSchema
    _output_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService
    _view_cls = EmployeeView

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__currency_service = CurrencyService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        self._open_loading_dialog()
        if event.key == View.EMPLOYEES:
            translation_service = self._state_store.app_state.translation
            self._key = event.key
            if event.data:
                mode = ViewMode.READ
                self._request_data.input_values = event.data
            else:
                mode = ViewMode.SEARCH
            currency_schemas = await self.__get_all_currencies()
            department_schemas = await self.__get_all_departments()
            employee_schemas = await self.__get_all_employees()
            self._view = EmployeeView(self, translation_service.items, mode, event.key, event.data)
            await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()

    async def _perform_get_page(self) -> PaginatedResponseSchema[EmployeePlainSchema]:
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
            endpoint=Endpoint.POSITIONS,
            query_params=params,
            view_key=self._key,
        )

    async def _perform_get_one(self, id: int) -> EmployeePlainSchema:
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_one,
            endpoint=Endpoint.POSITIONS,
            path_param=id,
            view_key=self._key,
        )

    async def _perform_create(self) -> EmployeePlainSchema:
        data = EmployeeStrictSchema(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.create,
            endpoint=Endpoint.POSITIONS,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_update(self, id: int) -> EmployeePlainSchema:
        data = EmployeeStrictSchema(**self._request_data.input_values)
        return await self._service.call_api_with_token_refresh(
            func=self._service.update,
            endpoint=Endpoint.POSITIONS,
            path_param=id,
            body_params=data,
            view_key=self._key,
        )

    async def _perform_delete(self, id: int) -> bool:
        return await self._service.call_api_with_token_refresh(
            func=self._service.delete,
            endpoint=Endpoint.POSITIONS,
            path_param=id,
            view_key=self._key,
        )

    async def __get_all_employees(self) -> list[EmployeePlainSchema]:
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_all,
            endpoint=Endpoint.EMPLOYEES,
            view_key=self._key,
        )

    async def __get_all_currencies(self) -> list[CurrencyPlainSchema]:
        return await self.__currency_service.call_api_with_token_refresh(
            func=self.__currency_service.get_all,
            endpoint=Endpoint.CURRENCIES,
            view_key=self._key,
        )

    async def __get_all_departments(self) -> list[DepartmentPlainSchema]:
        return await self.__department_service.call_api_with_token_refresh(
            func=self.__department_service.get_all,
            endpoint=Endpoint.DEPARTMENTS,
            view_key=self._key,
        )
