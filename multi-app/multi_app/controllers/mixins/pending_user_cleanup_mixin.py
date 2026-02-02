from __future__ import annotations

from typing import Any

from events.events import TabClosed
from services.core import UserService
from utils.enums import Endpoint, View, ViewMode


class PendingUserCleanupMixin:
    def _init_pending_user_cleanup(self) -> None:
        self.__pending_user_cleanup_in_progress = False
        self._subscribe_event_handlers({TabClosed: self.__pending_user_tab_closed_handler})
        self._subscribe_state_listeners({"view": self.__pending_user_view_updated_listener})

    def on_back_clicked(self) -> None:  # type: ignore[override]
        if not self._view:
            return
        if self.__should_cleanup_pending_user():
            self._page.run_task(self.__handle_pending_user_navigation, ViewMode.SEARCH)
            return
        super().on_back_clicked()

    def on_cancel_clicked(self) -> None:  # type: ignore[override]
        if not self._view:
            return
        if self.__should_cleanup_pending_user():
            target_mode = ViewMode.SEARCH if self._view.mode == ViewMode.CREATE else ViewMode.READ
            self._page.run_task(self.__handle_pending_user_navigation, target_mode)
            return
        super().on_cancel_clicked()

    async def __handle_pending_user_navigation(self, target_mode: ViewMode) -> None:
        proceed = await self.__cleanup_pending_user()
        if not proceed:
            return
        if not self._view:
            return
        if target_mode == ViewMode.SEARCH:
            self._view.search_results = None
        self._state_store.update(view={"mode": target_mode})
        self._view.clear_inputs()

    def __should_cleanup_pending_user(self) -> bool:
        if not self._view:
            return False
        if self._view.view_key != View.EMPLOYEES:
            return False
        if self._view.mode != ViewMode.CREATE:
            return False
        return isinstance(self._request_data.pending_user_id, int)

    async def __cleanup_pending_user(self) -> bool:
        if self.__pending_user_cleanup_in_progress:
            return False
        pending_user_id = self._request_data.pending_user_id
        if not isinstance(pending_user_id, int):
            return True
        self.__pending_user_cleanup_in_progress = True
        try:
            confirm = await self._show_confirm_dialog("confirm_delete_pending_user")
            if not confirm:
                return False
            self._request_data.pending_user_id = None
            await self._perform_delete(
                pending_user_id,
                UserService(self._settings, self._logger, self._tokens_accessor),
                Endpoint.USERS,
            )
            return True
        finally:
            self.__pending_user_cleanup_in_progress = False

    async def can_close_tab(self, view: Any) -> bool:
        if view is not self._view:
            return True
        if not self.__should_cleanup_pending_user():
            return True
        return await self.__cleanup_pending_user()

    async def __pending_user_tab_closed_handler(self, event: TabClosed) -> None:
        if event.view.view_key != View.EMPLOYEES:
            return
        if self._view is not event.view:
            return
        if self.__should_cleanup_pending_user():
            await self.__cleanup_pending_user()

    def __pending_user_view_updated_listener(self, state: Any) -> None:
        if not getattr(state, "title", None):
            return
        if not hasattr(state, "view"):
            return
        if state.view is not self._view:
            return
        if self._view.mode == ViewMode.CREATE and state.mode != ViewMode.CREATE:
            if self.__should_cleanup_pending_user():
                self._page.run_task(self.__handle_pending_user_navigation, state.mode)

