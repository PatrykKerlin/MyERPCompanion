import asyncio
from typing import Any

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from schemas.core.assoc_user_group_schema import AssocUserGroupPlainSchema, AssocUserGroupStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema
from services.core import AssocUserGroupService, GroupService, LanguageService, UserService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.user_view import UserView
from events.events import ViewRequested


class UserController(BaseViewController[UserService, UserView, UserPlainSchema, UserStrictUpdateSchema]):
    _plain_schema_cls = UserPlainSchema
    _strict_schema_cls = UserStrictUpdateSchema
    _service_cls = UserService
    _view_cls = UserView
    _endpoint = Endpoint.USERS
    _view_key = View.USERS

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__group_service = GroupService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_user_group_service = AssocUserGroupService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> UserView:
        groups: list[GroupPlainSchema] = []
        if event.data and mode in {ViewMode.READ, ViewMode.EDIT}:
            languages, groups = await asyncio.gather(
                self.__perform_get_all_languages(),
                self.__perform_get_all_groups(),
            )
        else:
            languages = await self.__perform_get_all_languages()
        language_pairs = [(language.id, language.key) for language in languages]
        theme_pairs = [
            ("system", translation.get("system")),
            ("dark", translation.get("dark")),
            ("light", translation.get("light")),
        ]
        group_source_rows: list[tuple[int, list[str]]] = []
        group_target_rows: list[tuple[int, list[str]]] = []
        if event.data and mode in {ViewMode.READ, ViewMode.EDIT}:
            group_source_rows, group_target_rows = self.__build_group_rows(groups, event.data)
        return UserView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            language_pairs,
            theme_pairs,
            group_source_rows,
            group_target_rows,
            on_groups_save_clicked=self.on_groups_save_clicked,
            on_groups_delete_clicked=self.on_groups_delete_clicked,
        )

    def on_save_clicked(self) -> None:
        if self._view and self._view.mode == ViewMode.CREATE:
            self._strict_schema_cls = UserStrictCreateSchema
        else:
            self._strict_schema_cls = UserStrictUpdateSchema
        self._page.run_task(self._BaseViewController__execute_save_clicked)

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
