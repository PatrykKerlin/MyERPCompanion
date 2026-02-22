import asyncio
from typing import Any

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.core.assoc_module_group_schema import AssocModuleGroupPlainSchema, AssocModuleGroupStrictSchema
from schemas.core.assoc_view_controller_schema import AssocViewControllerStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core import AssocModuleGroupService, AssocViewControllerService, GroupService, ModuleService, ViewService
from utils.enums import ApiActionError, Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.module_view import ModuleView


class ModuleController(BaseViewController[ModuleService, ModuleView, ModulePlainSchema, ModuleStrictSchema]):
    _plain_schema_cls = ModulePlainSchema
    _strict_schema_cls = ModuleStrictSchema
    _service_cls = ModuleService
    _view_cls = ModuleView
    _endpoint = Endpoint.MODULES
    _view_key = View.MODULES

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__view_service = ViewService(self._settings, self._logger, self._tokens_accessor)
        self.__group_service = GroupService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_module_group_service = AssocModuleGroupService(self._settings, self._logger, self._tokens_accessor)
        self.__assoc_view_controller_service = AssocViewControllerService(
            self._settings, self._logger, self._tokens_accessor
        )

    def on_views_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view or not self._view.data_row:
            return
        module_id = self._view.data_row["id"]
        pending = self._view.get_pending_view_targets()
        if not pending:
            return
        self._page.run_task(self.__handle_views_save, module_id, pending)

    def on_views_delete_clicked(self, view_ids: list[int]) -> None:
        if not self._view or not view_ids:
            return
        self._page.run_task(self.__handle_views_delete, view_ids)

    def on_groups_save_clicked(self, _: ft.Event[ft.IconButton]) -> None:
        if not self._view or not self._view.data_row:
            return
        module_id = self._view.data_row["id"]
        pending = self._view.get_pending_group_targets_with_permissions()
        if not pending:
            return
        self._page.run_task(self.__handle_groups_save, module_id, pending)

    def on_groups_delete_clicked(self, group_ids: list[int]) -> None:
        if not self._view or not group_ids or not self._view.data_row:
            return
        module_id = self._view.data_row["id"]
        self._page.run_task(self.__handle_groups_delete, module_id, group_ids)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ModuleView:
        source_rows: list[tuple[int, list[str]]] = []
        target_rows: list[tuple[int, list[str]]] = []
        group_source_rows: list[tuple[int, list[str]]] = []
        group_target_rows: list[tuple[int, list[str]]] = []
        if event.data and mode in {ViewMode.READ, ViewMode.EDIT}:
            views, groups, group_assocs = await asyncio.gather(
                self.__perform_get_all_views(),
                self.__perform_get_all_groups(),
                self.__perform_get_module_group_assocs(event.data.get("id")),
            )
            source_rows, target_rows = self.__build_view_rows(views, event.data)
            group_source_rows, group_target_rows = self.__build_group_rows(groups, group_assocs)
        return ModuleView(
            self,
            translation,
            mode,
            event.view_key,
            event.data,
            source_views=source_rows,
            target_views=target_rows,
            group_source_rows=group_source_rows,
            group_target_rows=group_target_rows,
            on_views_save_clicked=self.on_views_save_clicked,
            on_views_delete_clicked=self.on_views_delete_clicked,
            on_groups_save_clicked=self.on_groups_save_clicked,
            on_groups_delete_clicked=self.on_groups_delete_clicked,
        )

    async def __handle_views_save(self, module_id: int, pending: list[tuple[int, int]]) -> None:
        if not self._view or not self._view.data_row:
            return
        all_views = await self.__perform_get_all_views()
        views_by_id = {view.id: view for view in all_views}
        max_order = max((view.order for view in all_views if view.module_id == module_id), default=0)
        create_payloads: list[ViewStrictSchema] = []
        create_sources: list[ViewPlainSchema] = []
        for _, source_id in pending:
            view = views_by_id.get(source_id)
            if not view:
                continue
            max_order += 1
            create_payloads.append(
                ViewStrictSchema(
                    key=view.key,
                    description=view.description,
                    order=max_order,
                    module_id=module_id,
                )
            )
            create_sources.append(view)
        if not create_payloads:
            return
        created_views = await self.__perform_create_views(create_payloads)
        if not created_views:
            return
        controllers_created_count = await self.__perform_create_view_controllers(created_views, create_sources)
        if controllers_created_count is None:
            return
        await self.__refresh_view_rows(module_id)

    async def __handle_views_delete(self, view_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        module_id = self._view.data_row["id"]
        deletable_ids: list[int] = []
        blocked_keys: set[str] = set()
        for view_id in view_ids:
            view_key = self._view.get_target_key_by_id(view_id)
            if not view_key:
                continue
            response = await self.__perform_get_views_by_key(view_key)
            if response.total > 1:
                deletable_ids.append(view_id)
            else:
                blocked_keys.add(view_key)

        if deletable_ids:
            deleted = await self.__perform_delete_views(deletable_ids)
            if not deleted:
                return

        if blocked_keys:
            blocked_list = ", ".join(sorted(blocked_keys))
            self._open_error_dialog(message=f"Cannot delete last view for key(s): {blocked_list}")

        await self.__refresh_view_rows(module_id)

    async def __handle_groups_save(self, module_id: int, pending: list[tuple[int, int, bool, bool]]) -> None:
        if not self._view or not self._view.data_row:
            return
        updates = [
            AssocModuleGroupStrictSchema(
                module_id=module_id,
                group_id=group_id,
                can_read=can_read,
                can_modify=can_modify,
            )
            for _, group_id, can_read, can_modify in pending
        ]
        if not updates:
            return
        created = await self.__perform_create_module_groups(updates)
        if not created:
            return
        await self.__refresh_group_rows(module_id)

    async def __handle_groups_delete(self, module_id: int, group_ids: list[int]) -> None:
        if not self._view or not self._view.data_row:
            return
        assoc_rows = await self.__perform_get_module_group_assocs(module_id)
        assoc_by_group = {item.group_id: item.id for item in assoc_rows}
        delete_ids = [assoc_by_group[group_id] for group_id in group_ids if group_id in assoc_by_group]
        if delete_ids:
            deleted = await self.__perform_delete_module_groups(delete_ids)
            if not deleted:
                return
        await self.__refresh_group_rows(module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_views(self) -> list[ViewPlainSchema]:
        return await self.__view_service.get_all(Endpoint.VIEWS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_views_by_key(self, view_key: str) -> PaginatedResponseSchema[ViewPlainSchema]:
        return await self.__view_service.get_page(
            Endpoint.VIEWS, None, {"page": 1, "page_size": 2, "key": view_key}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_views(self, payload: list[ViewStrictSchema]) -> list[ViewPlainSchema]:
        return await self.__view_service.create_bulk(Endpoint.VIEWS_CREATE_BULK, None, None, payload, self._module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_view_controllers(
        self, created_views: list[ViewPlainSchema], source_views: list[ViewPlainSchema]
    ) -> int | None:
        if not created_views or not source_views:
            return 0
        payload: list[AssocViewControllerStrictSchema] = []
        for created_view, source_view in zip(created_views, source_views):
            for controller_id in source_view.controller_ids:
                payload.append(AssocViewControllerStrictSchema(view_id=created_view.id, controller_id=controller_id))
        if not payload:
            return 0
        await self.__assoc_view_controller_service.create_bulk(
            Endpoint.VIEW_CONTROLLERS_CREATE_BULK, None, None, payload, self._module_id
        )
        return len(payload)

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_views(self, view_ids: list[int]) -> bool:
        await self.__view_service.delete_bulk(
            Endpoint.VIEWS_DELETE_BULK, None, None, IdsPayloadSchema(ids=view_ids), self._module_id
        )
        return True

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_groups(self) -> list[GroupPlainSchema]:
        return await self.__group_service.get_all(Endpoint.GROUPS, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_module_group_assocs(self, module_id: int) -> list[AssocModuleGroupPlainSchema]:
        return await self.__assoc_module_group_service.get_all(
            Endpoint.MODULE_GROUPS, None, {"module_id": module_id}, None, self._module_id
        )

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_create_module_groups(self, payload: list[AssocModuleGroupStrictSchema]) -> bool:
        await self.__assoc_module_group_service.create_bulk(
            Endpoint.MODULE_GROUPS_CREATE_BULK, None, None, payload, self._module_id
        )
        return True

    @BaseController.handle_api_action(ApiActionError.DELETE)
    async def __perform_delete_module_groups(self, assoc_ids: list[int]) -> bool:
        await self.__assoc_module_group_service.delete_bulk(
            Endpoint.MODULE_GROUPS_DELETE_BULK,
            None,
            None,
            IdsPayloadSchema(ids=assoc_ids),
            self._module_id,
        )
        return True

    def __build_view_rows(
        self,
        all_views: list[ViewPlainSchema],
        data_row: dict[str, Any] | None,
    ) -> tuple[list[tuple[int, list[str]]], list[tuple[int, list[str]]]]:
        module_views_raw = data_row.get("views", []) if data_row else []
        module_views = [ViewPlainSchema.model_validate(item) for item in module_views_raw]
        target_ids = {view.id for view in module_views}
        module_keys = {view.key for view in module_views}

        rows = [
            (view.id, [view.key, view.description or "", str(view.order)])
            for view in sorted(all_views, key=lambda item: item.order)
        ]
        target_rows = [(view_id, values) for view_id, values in rows if view_id in target_ids]

        source_rows: list[tuple[int, list[str]]] = []
        seen_keys: set[str] = set()
        for view in sorted(all_views, key=lambda item: item.key):
            if view.key in module_keys or view.key in seen_keys:
                continue
            seen_keys.add(view.key)
            source_rows.append((view.id, [view.key, view.description or "", str(view.order)]))

        return source_rows, target_rows

    def __build_group_rows(
        self, groups: list[GroupPlainSchema], assocs: list[AssocModuleGroupPlainSchema]
    ) -> tuple[list[tuple[int, list[str]]], list[tuple[int, list[str]]]]:
        assoc_by_group = {assoc.group_id: assoc for assoc in assocs}
        target_ids = {assoc.group_id for assoc in assocs}
        target_rows: list[tuple[int, list[str]]] = []
        for group in groups:
            assoc = assoc_by_group.get(group.id)
            if not assoc:
                continue
            target_rows.append(
                (
                    group.id,
                    [
                        group.key,
                        group.description or "",
                        str(assoc.can_read),
                        str(assoc.can_modify),
                    ],
                )
            )
        source_rows = [
            (group.id, [group.key, group.description or ""]) for group in groups if group.id not in target_ids
        ]
        return source_rows, target_rows

    async def __refresh_view_rows(self, module_id: int) -> None:
        if not self._view:
            return
        updated_module, refreshed_views = await asyncio.gather(
            self._perform_get_one(module_id, self._service, self._endpoint),
            self.__perform_get_all_views(),
        )
        data_row = updated_module.model_dump()
        self._view._data_row = data_row
        source_rows, target_rows = self.__build_view_rows(refreshed_views, data_row)
        self._view.set_source_views(source_rows)
        self._view.set_target_views(target_rows)

    async def __refresh_group_rows(self, module_id: int) -> None:
        if not self._view:
            return
        updated_module, groups, group_assocs = await asyncio.gather(
            self._perform_get_one(module_id, self._service, self._endpoint),
            self.__perform_get_all_groups(),
            self.__perform_get_module_group_assocs(module_id),
        )
        data_row = updated_module.model_dump()
        self._view._data_row = data_row
        source_rows, target_rows = self.__build_group_rows(groups, group_assocs)
        self._view.set_group_source_rows(source_rows)
        self._view.set_group_target_rows(target_rows)
