from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_controller import BaseController
from events.events import AuthDialogRequested, AuthViewReady, UserAuthenticated
from services.core.auth_service import AuthService
from utils.enums import ApiActionError, Endpoint, Module
from views.core.auth_view import AuthView

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.token_schema import TokenPlainSchema
    from schemas.core.user_schema import UserPlainSchema


class AuthController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AuthService(self._settings, self._logger, self._tokens_accessor)
        self._subscribe_event_handlers({AuthDialogRequested: self.__auth_requested_handler})

    def on_login_click(self, username: str, password: str) -> None:
        self._page.run_task(self.__handle_login, username, password)

    async def __auth_requested_handler(self, _: AuthDialogRequested) -> None:
        translation_state = self._state_store.app_state.translation
        view = AuthView(controller=self, translation=translation_state.items)
        await self._event_bus.publish(AuthViewReady(component=view))

    async def __handle_login(self, username: str, password: str) -> None:
        tokens = await self.__perform_fetch_tokens(username, password)
        if not tokens:
            return
        self._state_store.update(tokens={"access": tokens.access, "refresh": tokens.refresh})
        user = await self.__perform_get_current_user()
        if not user:
            return
        self._state_store.update(user={"current": user})
        await self._event_bus.publish(AuthViewReady(component=None))
        await self._event_bus.publish(UserAuthenticated())

    @BaseController.handle_api_action(ApiActionError.INVALID_CREDENTIALS)
    async def __perform_fetch_tokens(self, username: str, password: str) -> TokenPlainSchema | None:
        return await self.__service.fetch_tokens(username, password)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_current_user(self) -> UserPlainSchema | None:
        return await self.__service.get_current_user(Endpoint.CURRENT_USER, None, None, None, Module.CORE)
