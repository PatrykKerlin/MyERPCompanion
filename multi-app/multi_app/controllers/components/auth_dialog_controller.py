from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from controllers.base.base_controller import BaseController
from events.events import AuthDialogRequested, AuthViewReady
from events.events import UserAuthenticated
from schemas.business.logistic.warehouse_schema import WarehouseLoginOptionSchema
from services.core.auth_service import AuthService
from utils.enums import ApiActionError, Endpoint
from views.components.auth_dialog_component import AuthDialogComponent
from views.mobile.auth_view import AuthView as MobileAuthView

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.module_schema import ModulePlainSchema
    from schemas.core.token_schema import TokenPlainSchema
    from schemas.core.user_schema import UserPlainSchema


class AuthDialogController(BaseComponentController[AuthDialogComponent, AuthDialogRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AuthService(self._settings, self._logger, self._tokens_accessor)
        self.__mobile_login_warehouses_request_id = 0
        self._subscribe_event_handlers({AuthDialogRequested: self._component_requested_handler})

    async def _component_requested_handler(self, _: AuthDialogRequested) -> None:
        translation_state = self._state_store.app_state.translation
        if self._settings.CLIENT == "mobile":
            self._component = MobileAuthView(controller=self, translation=translation_state.items)
            await self._event_bus.publish(AuthViewReady(component=self._component))
            self.on_mobile_username_changed(None)
            return
        self._component = AuthDialogComponent(controller=self, translation=translation_state.items)
        self._queue_dialog(self._component)

    def on_cancel_click(self) -> None:
        self._page.run_task(self._page.window.destroy)

    def on_login_click(self, username: str, password: str, warehouse_id: int | None = None) -> None:
        if self._settings.CLIENT in {"desktop", "mobile"}:
            self._page.run_task(self.__handle_login, "employee001", "test1234", warehouse_id)
        else:
            self._page.run_task(self.__handle_login, username, password, warehouse_id)

    def on_mobile_username_changed(self, username: str | None) -> None:
        if self._settings.CLIENT != "mobile":
            return
        self.__mobile_login_warehouses_request_id += 1
        request_id = self.__mobile_login_warehouses_request_id
        self._page.run_task(self.__load_mobile_login_warehouses, username, request_id)

    async def __handle_login(self, username: str, password: str, warehouse_id: int | None = None) -> None:
        tokens = await self.__perform_fetch_tokens(username, password, warehouse_id)
        if not tokens:
            return
        self._state_store.update(tokens={"access": tokens.access, "refresh": tokens.refresh})
        all_modules = await self.__perform_get_all_modules()
        if not all_modules:
            return
        user = await self.__perform_get_current_user()
        if not user:
            return
        if self._settings.CLIENT in {"desktop", "mobile"} and user.employee_id is None:
            self._state_store.update(tokens={"access": None, "refresh": None})
            self._open_error_dialog(message_key="employee_login_required")
            return
        user_groups_set = {group.id for group in user.groups}
        user_modules: list[ModulePlainSchema] = []
        for module in all_modules:
            module_groups_set = {group.id for group in module.groups}
            if module_groups_set.intersection(user_groups_set):
                user_modules.append(module)
        self._state_store.update(modules={"items": user_modules})
        self._state_store.update(user={"current": user})
        if self._component and self._settings.CLIENT == "desktop":
            self._page.pop_dialog()
        if self._settings.CLIENT == "mobile":
            self._component = None
            await self._event_bus.publish(AuthViewReady(component=None))
        await self._event_bus.publish(UserAuthenticated())

    async def __load_mobile_login_warehouses(self, username: str | None, request_id: int) -> None:
        warehouses = await self.__perform_get_login_warehouses(username)
        if request_id != self.__mobile_login_warehouses_request_id:
            return
        if not isinstance(self._component, MobileAuthView):
            return
        if warehouses is None:
            self._component.set_warehouse_options([])
            self._page.update()
            return
        options = [(warehouse.id, warehouse.name) for warehouse in warehouses]
        self._component.set_warehouse_options(options)
        self._page.update()

    @BaseController.handle_api_action(ApiActionError.INVALID_CREDENTIALS)
    async def __perform_fetch_tokens(
        self,
        username: str,
        password: str,
        warehouse_id: int | None = None,
    ) -> TokenPlainSchema | None:
        return await self.__service.fetch_tokens(username, password, warehouse_id)

    async def __perform_get_login_warehouses(
        self, username: str | None
    ) -> list[WarehouseLoginOptionSchema] | None:
        try:
            return await self.__service.get_login_warehouses(username)
        except Exception:
            self._logger.exception("Failed to load login warehouses for mobile auth")
            return None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_modules(self) -> list[ModulePlainSchema] | None:
        return await self.__service.get_all_modules(Endpoint.MODULES, None, None, None, self._module_id)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_current_user(self) -> UserPlainSchema | None:
        return await self.__service.get_current_user(Endpoint.CURRENT_USER, None, None, None, self._module_id)
