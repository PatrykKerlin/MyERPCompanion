from __future__ import annotations

from typing import Any

import flet as ft
from controllers.base.base_controller import BaseController
from events.events import CallerActionRequested, TabRequested
from schemas.business.hr.employee_schema import EmployeePlainSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema
from schemas.core.user_schema import UserPlainSchema
from services.business.hr import EmployeeService
from services.business.trade import CustomerService
from services.core import UserService
from utils.enums import ApiActionError, Endpoint, View, ViewMode


class UserLinkControllerMixin:
    def on_add_user_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view or self._view.mode != ViewMode.READ:
            return
        if self._view.data_row and self._view.data_row.get("user_id") is not None:
            return
        self._page.run_task(self._open_user_create_tab)

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

    def _init_user_link_mixin(self) -> None:
        self._subscribe_event_handlers({CallerActionRequested: self._handle_user_link_caller_action})
        self._user_link_user_service = UserService(self._settings, self._logger, self._tokens_accessor)
        self._user_link_employee_service = EmployeeService(self._settings, self._logger, self._tokens_accessor)
        self._user_link_customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)

    @property
    def _user_link_view_key(self) -> View:
        raise NotImplementedError

    @property
    def _user_link_entity_key(self) -> str:
        raise NotImplementedError

    async def _open_user_create_tab(self) -> None:
        if not self._view or self._view.mode != ViewMode.READ:
            return
        entity_id = None
        if self._view.data_row:
            entity_id = self._view.data_row.get("id")
        caller_data = {self._user_link_entity_key: entity_id} if isinstance(entity_id, int) else None
        await self._event_bus.publish(
            TabRequested(
                module_id=self._module_id,
                view_key=View.USERS,
                mode=ViewMode.CREATE,
                caller_view_key=self._user_link_view_key,
                caller_data=caller_data,
            )
        )

    async def _handle_user_link_caller_action(self, event: CallerActionRequested) -> None:
        if event.caller_view_key != self._user_link_view_key:
            return
        if event.source_view_key != View.USERS:
            return
        if not self._view:
            return
        if event.caller_data and isinstance(event.caller_data.get(self._user_link_entity_key), int):
            entity_id = event.caller_data.get(self._user_link_entity_key)
            if not self._view.data_row or self._view.data_row.get("id") != entity_id:
                return
        created_id = event.created_id
        username = None
        if event.record_data:
            username = event.record_data.get("username")
        if not username:
            users = await self._perform_get_all_users()
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

    @staticmethod
    def _normalize_user_link_id(value: int | str | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        value_str = str(value).strip()
        if not value_str or value_str == "0":
            return None
        return int(value_str) if value_str.isdigit() else None

    def _build_user_link_options(
        self,
        users: list[UserPlainSchema],
        employees: list[EmployeePlainSchema],
        customers: list[CustomerPlainSchema],
        data_row: dict[str, Any] | None,
    ) -> list[tuple[int, str]]:
        current_user_id = self._normalize_user_link_id(data_row.get("user_id") if data_row else None)
        if current_user_id is None:
            return []
        if self._user_link_entity_key == "employee_id":
            used_user_ids = {employee.user_id for employee in employees if employee.user_id}
        else:
            used_user_ids = {customer.user_id for customer in customers if customer.user_id}
        if current_user_id in used_user_ids:
            used_user_ids.discard(current_user_id)
        options: list[tuple[int, str]] = []
        for user in users:
            if user.id == 1:
                continue
            if user.id in used_user_ids:
                continue
            options.append((user.id, user.username))
        if current_user_id not in {item[0] for item in options}:
            for user in users:
                if user.id == current_user_id:
                    options.append((user.id, user.username))
                    break
        return options

    def _build_user_link_search_options(
        self,
        users: list[UserPlainSchema],
        employees: list[EmployeePlainSchema],
        customers: list[CustomerPlainSchema],
    ) -> list[tuple[int, str]]:
        if self._user_link_entity_key == "employee_id":
            assigned_user_ids = {employee.user_id for employee in employees if employee.user_id}
        else:
            assigned_user_ids = {customer.user_id for customer in customers if customer.user_id}
        return [(user.id, user.username) for user in users if user.id in assigned_user_ids]

    def _get_user_link_options(
        self,
        mode: ViewMode,
        event: Any,
        users: list[UserPlainSchema],
        employees: list[EmployeePlainSchema],
        customers: list[CustomerPlainSchema],
    ) -> list[tuple[int, str]]:
        if mode == ViewMode.SEARCH:
            return self._build_user_link_search_options(users, employees, customers)
        data_row = event.data if isinstance(event.data, dict) else None
        if mode == ViewMode.CREATE and event.caller_view_key == self._user_link_view_key:
            return []
        return self._build_user_link_options(users, employees, customers, data_row)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_all_users(self) -> list[UserPlainSchema]:
        return await self._user_link_user_service.get_all(Endpoint.USERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_all_employees(self) -> list[EmployeePlainSchema]:
        return await self._user_link_employee_service.get_all(Endpoint.EMPLOYEES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def _perform_get_all_customers(self) -> list[CustomerPlainSchema]:
        return await self._user_link_customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)
