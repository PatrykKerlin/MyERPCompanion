import asyncio
from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from controllers.mixins.user_link_controller_mixin import UserLinkControllerMixin
from events.events import ViewRequested
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.position_schema import PositionPlainSchema
from services.business.hr import DepartmentService, EmployeeService, PositionService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.hr.employee_view import EmployeeView


class EmployeeController(
    UserLinkControllerMixin,
    BaseViewController[EmployeeService, EmployeeView, EmployeePlainSchema, EmployeeStrictSchema],
):
    _plain_schema_cls = EmployeePlainSchema
    _strict_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService
    _view_cls = EmployeeView
    _endpoint = Endpoint.EMPLOYEES
    _view_key = View.EMPLOYEES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._init_user_link_mixin()
        self.__position_service = PositionService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)
        self.__all_departments: list[DepartmentPlainSchema] = []
        self.__all_positions: list[PositionPlainSchema] = []
        self.__all_employees: list[EmployeePlainSchema] = []
        self.__positions_by_id: dict[int, PositionPlainSchema] = {}

    @property
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

    def get_search_result_columns(self, available_fields: list[str]) -> list[str]:
        return [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "hire_date",
            "termination_date",
            "is_remote",
        ]

    @property
    def _user_link_view_key(self) -> View:
        return View.EMPLOYEES

    @property
    def _user_link_entity_key(self) -> str:
        return "employee_id"

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> EmployeeView:
        (
            self.__all_employees,
            self.__all_departments,
            self.__all_positions,
            users,
        ) = await asyncio.gather(
            self.__perform_get_all_employees(),
            self.__perform_get_all_departments(),
            self.__perform_get_all_positions(),
            self._perform_get_all_users(),
        )
        self.__positions_by_id = {position.id: position for position in self.__all_positions}

        selected_department_id = self._request_data.input_values.get("department_id")
        selected_position_id = self._request_data.input_values.get("position_id")
        data_row = dict(event.data) if event.data else None
        if mode == ViewMode.SEARCH:
            user_options = self._get_user_link_options(mode, event, users, self.__all_employees, [])
            departments = [(department.id, department.name) for department in self.__all_departments]
            positions = [(position.id, position.name) for position in self.__all_positions]
            managers = [
                (employee.id, f"{employee.first_name} {employee.last_name}") for employee in self.__all_employees
            ]
        else:
            user_options = self._get_user_link_options(mode, event, users, self.__all_employees, [])
            positions_filtered = self.__filter_positions_by_department(selected_department_id)
            departments = [(department.id, department.name) for department in self.__all_departments]
            positions = [(position.id, position.name) for position in positions_filtered]
            managers_filtered = self.__filter_managers_by_position(selected_position_id)
            managers = [(employee.id, f"{employee.first_name} {employee.last_name}") for employee in managers_filtered]
            current_manager_id = data_row.get("manager_id") if data_row else None
            if isinstance(current_manager_id, int) and current_manager_id not in {emp.id for emp in managers_filtered}:
                for employee in self.__all_employees:
                    if employee.id == current_manager_id:
                        managers.append((employee.id, f"{employee.first_name} {employee.last_name}"))
                        break

        subordinate_rows: list[dict[str, Any]] = []
        if data_row and mode in {ViewMode.READ, ViewMode.EDIT}:
            subordinate_ids = data_row.get("subordinate_ids")
            if isinstance(subordinate_ids, list):
                id_set = {item for item in subordinate_ids if isinstance(item, int)}
                if id_set:
                    for employee in self.__all_employees:
                        if employee.id in id_set:
                            subordinate_rows.append(
                                {
                                    "id": employee.id,
                                    "first_name": employee.first_name,
                                    "last_name": employee.last_name,
                                }
                            )
        return EmployeeView(
            self,
            translation,
            mode,
            event.view_key,
            data_row,
            departments,
            positions,
            managers,
            user_options,
            subordinate_rows,
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_employees(self) -> list[EmployeePlainSchema]:
        return await self._service.get_all(self._endpoint, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_positions(self) -> list[PositionPlainSchema]:
        return await self.__position_service.get_all(Endpoint.POSITIONS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_departments(self) -> list[DepartmentPlainSchema]:
        return await self.__department_service.get_all(Endpoint.DEPARTMENTS, None, None, None, self._module_id)

    def __filter_positions_by_department(self, department_id: int | str | None) -> list[PositionPlainSchema]:
        if department_id is None:
            return self.__all_positions
        return [position for position in self.__all_positions if position.department_id == department_id]

    def __filter_managers_by_position(self, position_id: int | str | None) -> list[EmployeePlainSchema]:
        if position_id is None or position_id not in self.__positions_by_id:
            return self.__all_employees
        base_level = self.__positions_by_id[position_id].level
        result: list[EmployeePlainSchema] = []
        for employee in self.__all_employees:
            position = self.__positions_by_id.get(employee.position_id)
            if position and position.level > base_level:
                result.append(employee)
        return result
