from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from services.core.auth_service import AuthService
from views.components.auth_dialog_component import AuthDialogComponent
from events.events import AuthDialogRequested
from utils.enums import View
from events.events import UserAuthenticated

if TYPE_CHECKING:
    from config.context import Context


class AuthDialogController(BaseComponentController[AuthDialogComponent, AuthDialogRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AuthService(self._settings)
        self._subscribe_event_handlers({AuthDialogRequested: self._component_requested_handler})

    async def _component_requested_handler(self, _: AuthDialogRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = AuthDialogComponent(controller=self, translation=translation_state.items)
        self._open_dialog(self._component)

    def on_cancel_click(self) -> None:
        self._page.window.destroy()

    def on_login_click(self, username: str, password: str) -> None:
        self._page.run_task(self.__handle_login, "user1", "test1234")

    async def __handle_login(self, username: str, password: str) -> None:
        try:
            tokens = await self.__service.fetch_tokens(username, password)
            self._state_store.update(tokens={"access": tokens.access, "refresh": tokens.refresh})
            modules = await self._call_with_refresh(
                service=self.__service, func=self.__service.fetch_modules, view_key=View.SIDE_MENU
            )
            self._state_store.update(modules={"items": modules})
            user = await self._call_with_refresh(
                service=self.__service, func=self.__service.fetch_current_user, view_key=View.CURRENT_USER
            )
            self._state_store.update(user={"current": user})
            if self._component:
                self._close_dialog(self._component)
            await self._event_bus.publish(UserAuthenticated())
        except Exception as error:
            self._logger.error(error)
            if self._component:
                self._close_dialog(self._component)
            # self._show_error_dialog(message=str(error))
