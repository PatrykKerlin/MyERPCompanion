from config.context import Context
from controllers.base.base_view_controller import BaseViewController
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.hr.position_schema import PositionPlainSchema
from services.business.hr import DepartmentService, EmployeeService, PositionService
from utils.enums import Endpoint, View, ViewMode
from views.business.hr.employee_view import EmployeeView
from events.events import ViewRequested, ViewReady


class EmployeeController(BaseViewController[EmployeeService, EmployeeView, EmployeePlainSchema, EmployeeStrictSchema]):
    _input_schema_cls = EmployeePlainSchema
    _output_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService
    _view_cls = EmployeeView
    _endpoint = Endpoint.EMPLOYEES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__position_service = PositionService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)
        self.__all_departments: list[DepartmentPlainSchema] = []
        self.__all_positions: list[PositionPlainSchema] = []
        self.__all_employees: list[EmployeePlainSchema] = []
        self.__positions_by_id: dict[int, PositionPlainSchema] = {}
        self._subscribe_event_handlers(
            {
                ViewRequested: self._view_requested_handler,
            }
        )

    def on_department_changed(self) -> None:
        if not self._view:
            return
        department_id = self._request_data.input_values.get("department_id")
        positions = self.__filter_positions_by_department(department_id)
        self._view.set_dropdown_options("position_id", [(position.id, position.name) for position in positions])
        if self._request_data.input_values.get("position_id") not in {position.id for position in positions}:
            self._request_data.input_values["position_id"] = None
            self.on_position_changed()

    def on_position_changed(self) -> None:
        if not self._view:
            return
        position_id = self._request_data.input_values.get("position_id")
        managers = self.__filter_managers_by_position(position_id)
        self._view.set_dropdown_options(
            "manager_id", [(manager.id, f"{manager.first_name} {manager.last_name}") for manager in managers]
        )

    async def _view_requested_handler(self, event: ViewRequested) -> None:
        if event.key != View.EMPLOYEES:
            return
        self._open_loading_dialog()
        translation_service = self._state_store.app_state.translation
        self._key = event.key
        self.__all_departments = await self.__get_all_departments()
        self.__all_positions = await self.__perform_get_all_positions()
        self.__positions_by_id = {position.id: position for position in self.__all_positions}
        self.__all_employees = await self.__perform_get_all_employees()
        if event.data:
            mode = ViewMode.READ
            self._request_data.input_values = event.data
        else:
            mode = ViewMode.SEARCH

        selected_department_id = self._request_data.input_values.get("department_id")
        selected_position_id = self._request_data.input_values.get("position_id")

        if mode == ViewMode.SEARCH:
            departments_opts = [(department.id, department.name) for department in self.__all_departments]
            positions_opts = [(p.id, p.name) for p in self.__all_positions]
            managers_opts = [(e.id, f"{e.first_name} {e.last_name}") for e in self.__all_employees]
        else:
            dept_positions = self.__filter_positions_by_department(selected_department_id)
            departments_opts = [(department.id, department.name) for department in self.__all_departments]
            positions_opts = [(position.id, position.name) for position in dept_positions]
            managers = self.__filter_managers_by_position(selected_position_id)
            managers_opts = [(employee.id, f"{employee.first_name} {employee.last_name}") for employee in managers]

        self._view = EmployeeView(
            self,
            translation_service.items,
            mode,
            event.key,
            event.data,
            departments_opts,
            positions_opts,
            managers_opts,
        )
        await self._event_bus.publish(ViewReady(key=event.key, postfix=event.postfix, view=self._view))
        self._close_loading_dialog()

    async def __perform_get_all_employees(self) -> list[EmployeePlainSchema]:
        return await self._service.call_api_with_token_refresh(
            func=self._service.get_all,
            endpoint=self._endpoint,
            view_key=self._key,
        )

    async def __perform_get_all_positions(self) -> list[PositionPlainSchema]:
        return await self.__position_service.call_api_with_token_refresh(
            func=self.__position_service.get_all,
            endpoint=Endpoint.POSITIONS,
            view_key=self._key,
        )

    async def __get_all_departments(self) -> list[DepartmentPlainSchema]:
        return await self.__department_service.call_api_with_token_refresh(
            func=self.__department_service.get_all,
            endpoint=Endpoint.DEPARTMENTS,
            view_key=self._key,
        )

    def __filter_positions_by_department(self, department_id: int | None) -> list[PositionPlainSchema]:
        if department_id is None:
            return self.__all_positions
        return [position for position in self.__all_positions if position.department_id == department_id]

    def __filter_managers_by_position(self, position_id: int | None) -> list[EmployeePlainSchema]:
        if position_id is None or position_id not in self.__positions_by_id:
            return self.__all_employees
        base_level = self.__positions_by_id[position_id].level
        result: list[EmployeePlainSchema] = []
        for employee in self.__all_employees:
            position = self.__positions_by_id.get(employee.position_id)
            if position and position.level > base_level:
                result.append(employee)
        return result
