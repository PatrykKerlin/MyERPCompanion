import asyncio
from typing import Any

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.business.hr.employee_schema import EmployeePlainSchema, EmployeeStrictSchema
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.hr.position_schema import PositionPlainSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema
from schemas.core.user_schema import UserPlainSchema
from services.business.hr import DepartmentService, EmployeeService, PositionService
from services.business.trade import CustomerService
from services.core import UserService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.hr.employee_view import EmployeeView
from events.events import TabRequested, CallerActionRequested, ViewRequested

import flet as ft


class EmployeeController(BaseViewController[EmployeeService, EmployeeView, EmployeePlainSchema, EmployeeStrictSchema]):
    _plain_schema_cls = EmployeePlainSchema
    _strict_schema_cls = EmployeeStrictSchema
    _service_cls = EmployeeService
    _view_cls = EmployeeView
    _endpoint = Endpoint.EMPLOYEES
    _view_key = View.EMPLOYEES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers({CallerActionRequested: self.__caller_action_handler})
        self.__position_service = PositionService(self._settings, self._logger, self._tokens_accessor)
        self.__department_service = DepartmentService(self._settings, self._logger, self._tokens_accessor)
        self.__user_service = UserService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)
        self.__all_departments: list[DepartmentPlainSchema] = []
        self.__all_positions: list[PositionPlainSchema] = []
        self.__all_employees: list[EmployeePlainSchema] = []
        self.__positions_by_id: dict[int, PositionPlainSchema] = {}

    def on_add_user_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view or self._view.mode != ViewMode.READ:
            return
        if self._view.data_row and self._view.data_row.get("user_id") is not None:
            return
        self._page.run_task(self.__open_user_create_tab)

    def on_marker_clicked(self, event: ft.ControlEvent, key: str) -> None:
        super().on_marker_clicked(event, key)
        if key != "user_id" or not self._view:
            return
        field = self._view.inputs.get("user_id")
        if not field:
            return
        control = field.input.content
        dropdown: ft.Dropdown | None = None
        if isinstance(control, ft.Dropdown):
            dropdown = control
        elif isinstance(control, ft.Row):
            for item in control.controls:
                if isinstance(item, ft.Dropdown):
                    dropdown = item
                    break
        if dropdown is None:
            return
        marker_state = bool(getattr(event.control, "value", False))
        dropdown.disabled = not marker_state
        dropdown.update()


    def on_department_changed(self) -> None:
        if not self._view:
            return
        department_id = self.__normalize_id(self._request_data.input_values.get("department_id"))
        positions = self.__filter_positions_by_department(department_id)
        self._view.set_dropdown_options("position_id", [(position.id, position.name) for position in positions])
        if self._request_data.input_values.get("position_id") not in {position.id for position in positions}:
            self._request_data.input_values["position_id"] = None
            self.on_position_changed()

    def on_position_changed(self) -> None:
        if not self._view:
            return
        position_id = self.__normalize_id(self._request_data.input_values.get("position_id"))
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
    @staticmethod
    def __normalize_id(value: int | str | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        value_str = str(value).strip()
        if not value_str or value_str == '0':
            return None
        return int(value_str) if value_str.isdigit() else None



    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> EmployeeView:
        (
            self.__all_employees,
            self.__all_departments,
            self.__all_positions,
            users,
            customers,
        ) = await asyncio.gather(
            self.__perform_get_all_employees(),
            self.__perform_get_all_departments(),
            self.__perform_get_all_positions(),
            self.__perform_get_all_users(),
            self.__perform_get_all_customers(),
        )
        self.__positions_by_id = {position.id: position for position in self.__all_positions}

        selected_department_id = self.__normalize_id(self._request_data.input_values.get("department_id"))
        selected_position_id = self.__normalize_id(self._request_data.input_values.get("position_id"))
        data_row = dict(event.data) if event.data else None
        if mode == ViewMode.SEARCH:
            user_options = self.__build_search_user_options(users)
            departments = [(department.id, department.name) for department in self.__all_departments]
            positions = [(position.id, position.name) for position in self.__all_positions]
            managers = [
                (employee.id, f"{employee.first_name} {employee.last_name}") for employee in self.__all_employees
            ]
        else:
            if mode == ViewMode.CREATE and event.caller_view_key == View.EMPLOYEES:
                user_options = []
                if data_row is not None:
                    data_row["user_id"] = None
            else:
                user_options = self.__build_user_options(users, customers, data_row)
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

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_users(self) -> list[UserPlainSchema]:
        return await self.__user_service.get_all(Endpoint.USERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_customers(self) -> list[CustomerPlainSchema]:
        return await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)

    def __filter_positions_by_department(self, department_id: int | str | None) -> list[PositionPlainSchema]:
        department_id = self.__normalize_id(department_id)
        if department_id is None:
            return self.__all_positions
        return [position for position in self.__all_positions if position.department_id == department_id]

    def __filter_managers_by_position(self, position_id: int | str | None) -> list[EmployeePlainSchema]:
        position_id = self.__normalize_id(position_id)
        if position_id is None or position_id not in self.__positions_by_id:
            return self.__all_employees
        base_level = self.__positions_by_id[position_id].level
        result: list[EmployeePlainSchema] = []
        for employee in self.__all_employees:
            position = self.__positions_by_id.get(employee.position_id)
            if position and position.level > base_level:
                result.append(employee)
        return result

    def __build_user_options(
        self,
        users: list[UserPlainSchema],
        customers: list[CustomerPlainSchema],
        data_row: dict[str, Any] | None,
    ) -> list[tuple[int, str]]:
        current_user_id = self.__normalize_id(data_row.get("user_id") if data_row else None)
        if current_user_id is None:
            return []
        used_user_ids = {employee.user_id for employee in self.__all_employees if employee.user_id}
        used_user_ids.update({customer.user_id for customer in customers if customer.user_id})
        if current_user_id is not None and current_user_id in used_user_ids:
            used_user_ids.discard(current_user_id)
        options: list[tuple[int, str]] = []
        for user in users:
            if user.id == 1:
                continue
            if user.id in used_user_ids:
                continue
            options.append((user.id, user.username))
        if current_user_id is not None and current_user_id not in {item[0] for item in options}:
            for user in users:
                if user.id == current_user_id:
                    options.append((user.id, user.username))
                    break
        return options

    def __build_search_user_options(self, users: list[UserPlainSchema]) -> list[tuple[int, str]]:
        assigned_user_ids = {employee.user_id for employee in self.__all_employees if employee.user_id}
        return [(user.id, user.username) for user in users if user.id in assigned_user_ids]

    async def __open_user_create_tab(self) -> None:
        if not self._view or self._view.mode != ViewMode.READ:
            return
        employee_id = None
        if self._view.data_row:
            employee_id = self._view.data_row.get("id")
        caller_data = {"employee_id": employee_id} if isinstance(employee_id, int) else None
        await self._event_bus.publish(
            TabRequested(
                module_id=self._module_id,
                view_key=View.USERS,
                mode=ViewMode.CREATE,
                caller_view_key=View.EMPLOYEES,
                caller_data=caller_data,
            )
        )

    async def __caller_action_handler(self, event: CallerActionRequested) -> None:
        if event.caller_view_key != View.EMPLOYEES:
            return
        if event.source_view_key != View.USERS:
            return
        if not self._view:
            return
        if event.caller_data and isinstance(event.caller_data.get("employee_id"), int):
            employee_id = event.caller_data.get("employee_id")
            if not self._view.data_row or self._view.data_row.get("id") != employee_id:
                return
        created_id = event.created_id
        users, customers, employees = await asyncio.gather(
            self.__perform_get_all_users(),
            self.__perform_get_all_customers(),
            self.__perform_get_all_employees(),
        )
        self.__all_employees = employees
        username = None
        for user in users:
            if user.id == created_id:
                username = user.username
                break
        if username is None:
            return
        self._view.set_dropdown_options("user_id", [(created_id, username)])
        field = self._view.inputs.get("user_id") if self._view else None
        control = field.input.content if field else None
        dropdown: ft.Dropdown | None = None
        if isinstance(control, ft.Dropdown):
            dropdown = control
        elif isinstance(control, ft.Row):
            for item in control.controls:
                if isinstance(item, ft.Dropdown):
                    dropdown = item
                    break
        if dropdown is not None:
            dropdown.value = str(created_id)
            dropdown.update()
        self.set_field_value("user_id", created_id)
