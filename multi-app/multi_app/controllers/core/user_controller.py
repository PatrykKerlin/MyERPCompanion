import asyncio
from typing import Any, cast

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.core.assoc_user_group_schema import AssocUserGroupPlainSchema, AssocUserGroupStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateAppSchema, UserStrictUpdateAppSchema
from services.core import AssocUserGroupService, GroupService, LanguageService, UserService
from services.business.hr import EmployeeService
from services.business.trade import CustomerService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.user_view import UserView
from events.events import ViewRequested


class UserController(BaseViewController[UserService, UserView, UserPlainSchema, UserStrictUpdateAppSchema]):
    _plain_schema_cls = UserPlainSchema
    _strict_schema_cls = UserStrictUpdateAppSchema
    _service_cls = UserService
    _view_cls = UserView
    _endpoint = Endpoint.USERS
    _view_key = View.USERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__group_service = GroupService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_user_group_service = AssocUserGroupService(self._settings, self._logger, self._tokens_accessor)
        self.__employee_service = EmployeeService(self._settings, self._logger, self._tokens_accessor)
        self.__customer_service = CustomerService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UserView:
        groups: list[GroupPlainSchema] = []
        show_groups = event.module_id != 1
        show_relations = event.module_id != 1
        is_from_employees = event.caller_view_key == View.EMPLOYEES
        show_customer_relation = show_relations and not is_from_employees
        employee_locked_id = None
        if is_from_employees and event.caller_data:
            candidate = event.caller_data.get("employee_id")
            if isinstance(candidate, int):
                employee_locked_id = candidate
        data_row = dict(event.data) if event.data else None
        if employee_locked_id is not None:
            if data_row is None:
                data_row = {"employee_id": employee_locked_id}
            elif data_row.get("employee_id") is None:
                data_row["employee_id"] = employee_locked_id
            self._request_data.input_values["employee_id"] = employee_locked_id
        if data_row and mode in {ViewMode.READ, ViewMode.EDIT}:
            if show_relations:
                if show_customer_relation:
                    languages, groups, employees, customers, users = await asyncio.gather(
                        self.__perform_get_all_languages(),
                        self.__perform_get_all_groups(),
                        self.__perform_get_all_employees(),
                        self.__perform_get_all_customers(),
                        self.__perform_get_all_users(),
                    )
                else:
                    languages, groups, employees, users = await asyncio.gather(
                        self.__perform_get_all_languages(),
                        self.__perform_get_all_groups(),
                        self.__perform_get_all_employees(),
                        self.__perform_get_all_users(),
                    )
                    customers = []
            else:
                languages, groups = await asyncio.gather(
                    self.__perform_get_all_languages(),
                    self.__perform_get_all_groups(),
                )
                employees, customers, users = [], [], []
        else:
            if show_relations:
                if show_customer_relation:
                    languages, employees, customers, users = await asyncio.gather(
                        self.__perform_get_all_languages(),
                        self.__perform_get_all_employees(),
                        self.__perform_get_all_customers(),
                        self.__perform_get_all_users(),
                    )
                else:
                    languages, employees, users = await asyncio.gather(
                        self.__perform_get_all_languages(),
                        self.__perform_get_all_employees(),
                        self.__perform_get_all_users(),
                    )
                    customers = []
            else:
                languages = await self.__perform_get_all_languages()
                employees, customers, users = [], [], []
        language_pairs = [(language.id, language.key) for language in languages]
        used_employee_ids = {user.employee_id for user in users if user.employee_id is not None}
        used_customer_ids = {user.customer_id for user in users if user.customer_id is not None}
        current_employee_id = data_row.get("employee_id") if data_row else None
        current_customer_id = data_row.get("customer_id") if data_row else None
        if current_employee_id is not None and current_employee_id in used_employee_ids:
            used_employee_ids.discard(current_employee_id)
        if current_customer_id is not None and current_customer_id in used_customer_ids:
            used_customer_ids.discard(current_customer_id)
        employee_pairs = [
            (employee.id, f"{employee.first_name} {employee.last_name}")
            for employee in employees
            if employee.id not in used_employee_ids
        ]
        if employee_locked_id is not None:
            employee_pairs = [
                (employee.id, f"{employee.first_name} {employee.last_name}")
                for employee in employees
                if employee.id == employee_locked_id
            ]
        customer_pairs = [
            (customer.id, customer.company_name) for customer in customers if customer.id not in used_customer_ids
        ]
        if not show_customer_relation:
            customer_pairs = []
        if current_employee_id is not None and current_employee_id not in {item[0] for item in employee_pairs}:
            for employee in employees:
                if employee.id == current_employee_id:
                    employee_pairs.append((employee.id, f"{employee.first_name} {employee.last_name}"))
                    break
        if current_customer_id is not None and current_customer_id not in {item[0] for item in customer_pairs}:
            for customer in customers:
                if customer.id == current_customer_id:
                    customer_pairs.append((customer.id, customer.company_name))
                    break
        theme_pairs = [
            ("system", translation.get("system")),
            ("dark", translation.get("dark")),
            ("light", translation.get("light")),
        ]
        group_source_rows: list[tuple[int, list[str]]] = []
        group_target_rows: list[tuple[int, list[str]]] = []
        if show_groups and data_row and mode in {ViewMode.READ, ViewMode.EDIT}:
            group_source_rows, group_target_rows = self.__build_group_rows(groups, data_row)
        return UserView(
            self,
            translation,
            mode,
            event.view_key,
            data_row,
            language_pairs,
            theme_pairs,
            employee_pairs,
            customer_pairs,
            show_relations,
            show_customer_relation,
            employee_locked_id,
            group_source_rows,
            group_target_rows,
            show_groups,
            on_groups_save_clicked=self.on_groups_save_clicked,
            on_groups_delete_clicked=self.on_groups_delete_clicked,
        )

    def on_save_clicked(self) -> None:
        if self._view and self._view.mode == ViewMode.CREATE:
            self._strict_schema_cls = cast(type[UserStrictUpdateAppSchema], UserStrictCreateAppSchema)
        else:
            self._strict_schema_cls = UserStrictUpdateAppSchema
        super().on_save_clicked()

    def on_groups_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view or not self._view.data_row:
            return
        user_id = self._view.data_row["id"]
        pending = self._view.get_pending_group_targets()
        if not pending:
            return
        self._page.run_task(self.__handle_groups_save, user_id, pending)

    def on_groups_delete_clicked(self, group_ids: list[int]) -> None:
        if not self._view or not group_ids or not self._view.data_row:
            return
        user_id = self._view.data_row["id"]
        self._page.run_task(self.__handle_groups_delete, user_id, group_ids)

    async def __handle_groups_save(self, user_id: int, pending: list[tuple[int, int]]) -> None:
        if not self._view or not self._view.data_row:
            return
        updates = [AssocUserGroupStrictSchema(user_id=user_id, group_id=group_id) for _, group_id in pending]
        if not updates:
            return
        await self.__perform_create_user_groups(updates)
        await self.__refresh_group_rows(user_id)

    async def __handle_groups_delete(self, user_id: int, group_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        assoc_rows = await self.__perform_get_user_group_assocs(user_id)
        assoc_by_group = {item.group_id: item.id for item in assoc_rows}
        delete_ids = [assoc_by_group[group_id] for group_id in group_ids if group_id in assoc_by_group]
        if delete_ids:
            await self.__perform_delete_user_groups(delete_ids)
        await self.__refresh_group_rows(user_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_employees(self):
        return await self.__employee_service.get_all(Endpoint.EMPLOYEES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_customers(self):
        return await self.__customer_service.get_all(Endpoint.CUSTOMERS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_users(self) -> list[UserPlainSchema]:
        return await self._service.get_all(self._endpoint, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema]:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_groups(self) -> list[GroupPlainSchema]:
        return await self.__group_service.get_all(Endpoint.GROUPS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_user_groups(self, payload: list[AssocUserGroupStrictSchema]) -> None:
        await self.__assoc_user_group_service.create_bulk(
            Endpoint.USER_GROUPS_CREATE_BULK, None, None, payload, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_user_group_assocs(self, user_id: int) -> list[AssocUserGroupPlainSchema]:
        return await self.__assoc_user_group_service.get_all(
            Endpoint.USER_GROUPS, None, {"user_id": user_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_user_groups(self, assoc_ids: list[int]) -> None:
        await self.__assoc_user_group_service.delete_bulk(
            Endpoint.USER_GROUPS_DELETE_BULK,
            None,
            None,
            IdsPayloadSchema(ids=assoc_ids),
            self._module_id,
        )

    def __build_group_rows(
        self, groups: list[GroupPlainSchema], data_row: dict[str, Any] | None
    ) -> tuple[list[tuple[int, list[str]]], list[tuple[int, list[str]]]]:
        user_groups_raw = data_row.get("groups", []) if data_row else []
        user_groups = [GroupPlainSchema.model_validate(item) for item in user_groups_raw]
        target_ids = {group.id for group in user_groups}
        target_rows = [(group.id, [group.key, group.description or ""]) for group in user_groups]
        source_rows = [
            (group.id, [group.key, group.description or ""]) for group in groups if group.id not in target_ids
        ]
        return source_rows, target_rows

    async def __refresh_group_rows(self, user_id: int) -> None:
        if not self._view:
            return
        updated_user, groups = await asyncio.gather(
            self._perform_get_one(user_id, self._service, self._endpoint),
            self.__perform_get_all_groups(),
        )
        data_row = updated_user.model_dump()
        self._view._data_row = data_row
        source_rows, target_rows = self.__build_group_rows(groups, data_row)
        self._view.set_group_source_rows(source_rows)
        self._view.set_group_target_rows(target_rows)
