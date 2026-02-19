from __future__ import annotations

import asyncio
import time
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from config.context import Context
from httpx import HTTPStatusError
from schemas.base.base_schema import BaseStrictSchema
from utils.enums import ApiActionError
from utils.tokens_accessor import TokensAccessor
from views.components.error_dialog_component import ErrorDialogComponent
from views.components.loading_dialog_component import LoadingDialogComponent
from views.components.message_dialog_component import MessageDialogComponent

TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)
TReturn = TypeVar("TReturn")


class BaseController:
    _dialog_lock = asyncio.Lock()

    def __init__(self, context: Context) -> None:
        self._page = context.page
        self._settings = context.settings
        self._logger = context.logger
        self._event_bus = context.event_bus
        self._state_store = context.state_store
        self._tokens_accessor = TokensAccessor(self._state_store)
        self._loading_dialog: LoadingDialogComponent | None = None
        self._loading_min_visible_seconds = 0.25
        self.__loading_lock_acquired = False
        self.__loading_opened_at: float | None = None
        self.__loading_close_task: asyncio.Task[None] | None = None
        self.__unsubscribers: list[Callable[[], None]] = []
        self.__disposed: bool = False

    async def dispose(self) -> None:  # NOSONAR
        if self.__disposed:
            return
        self.__disposed = True
        while self.__unsubscribers:
            func = self.__unsubscribers.pop()
            func()

    @property
    def page(self) -> Any:
        return self._page

    def pop_dialog(self) -> Any:
        return self._page.pop_dialog()

    def queue_dialog(self, dialog: Any, wait_for_future: Awaitable[Any] | None = None) -> None:
        self._queue_dialog(dialog, wait_for_future)

    @classmethod
    def handle_api_action(
        cls, message_key: ApiActionError
    ) -> Callable[[Callable[..., Awaitable[TReturn]]], Callable[..., Awaitable[TReturn]]]:
        def decorator(func: Callable[..., Awaitable[TReturn]]) -> Callable[..., Awaitable[TReturn]]:
            @wraps(func)
            async def wrapper(self: BaseController, *args: Any, **kwargs: Any) -> TReturn:
                opened_loading = self._loading_dialog is None
                if opened_loading:
                    await self._open_loading_dialog()
                try:
                    result = await func(self, *args, **kwargs)
                    if opened_loading:
                        self._close_loading_dialog()
                    return result
                except HTTPStatusError as http_error:
                    self._close_loading_dialog()
                    self._logger.exception(f"HTTPStatusError in {func.__qualname__}")
                    if http_error.response.status_code == 403:
                        self._open_error_dialog(message_key="no_permissions")
                    else:
                        self._open_error_dialog(message_key=message_key)
                    return cast(TReturn, None)
                except Exception:
                    self._close_loading_dialog()
                    self._logger.exception(
                        f"Unhandled exception in {func.__qualname__}",
                    )
                    self._open_error_dialog(message_key=message_key)
                    return cast(TReturn, None)

            return wrapper

        return decorator

    async def _acquire_dialog_slot(self) -> None:
        await BaseController._dialog_lock.acquire()
        await self._wait_for_dialog_clear()

    def _close_loading_dialog(self) -> None:
        if not self._loading_dialog:
            if self.__loading_lock_acquired:
                self._release_dialog_slot()
                self.__loading_lock_acquired = False
            return
        if self.__loading_close_task is not None:
            return
        min_visible = getattr(self._loading_dialog, "min_visible_seconds", 0)
        if self.__loading_opened_at is None or min_visible <= 0:
            self.__finalize_loading_close()
            return
        elapsed = time.monotonic() - self.__loading_opened_at
        remaining = min_visible - elapsed
        if remaining <= 0:
            self.__finalize_loading_close()
            return
        self.__loading_close_task = asyncio.create_task(self.__close_loading_after_delay(remaining))

    def _open_error_dialog(self, message_key: str | None = None, message: str | None = None) -> None:
        translation = self._state_store.app_state.translation.items
        error_dialog = ErrorDialogComponent(
            translation=translation,
            message_key=message_key,
            message=message,
            on_ok_clicked=lambda _: self._page.pop_dialog(),
        )
        self._queue_dialog(error_dialog)

    async def _open_loading_dialog(self) -> None:
        acquired = await self._try_acquire_dialog_slot()
        if not acquired:
            return
        self.__loading_lock_acquired = True
        translation = self._state_store.app_state.translation.items
        self._loading_dialog = LoadingDialogComponent(
            translation,
            min_visible_seconds=self._loading_min_visible_seconds,
        )
        self.__loading_opened_at = time.monotonic()
        try:
            self._page.show_dialog(self._loading_dialog)
        except Exception:
            self._loading_dialog = None
            self.__loading_opened_at = None
            if self.__loading_lock_acquired:
                self._release_dialog_slot()
                self.__loading_lock_acquired = False
            raise

    def _open_message_dialog(self, message_key: str) -> None:
        translation = self._state_store.app_state.translation.items
        message_dialog = MessageDialogComponent(
            translation=translation,
            message_key=message_key,
            on_ok_clicked=lambda _: self._page.pop_dialog(),
        )
        self._queue_dialog(message_dialog)

    def _queue_dialog(self, dialog: Any, wait_for_future: Awaitable[Any] | None = None) -> None:
        try:
            self._page.run_task(self._show_dialog_serialized, dialog, wait_for_future)
        except (AttributeError, RuntimeError):
            self._logger.warning("Dialog fallback: showing without run_task", exc_info=True)
            self._page.show_dialog(dialog)

    def _release_dialog_slot(self) -> None:
        if BaseController._dialog_lock.locked():
            BaseController._dialog_lock.release()

    async def _show_dialog_serialized(
        self,
        dialog: Any,
        wait_for_future: Awaitable[Any] | None = None,
    ) -> None:
        await self._acquire_dialog_slot()
        try:
            self._page.show_dialog(dialog)
            if wait_for_future is not None:
                await wait_for_future
            else:
                await self._wait_for_dialog_closed(dialog)
        finally:
            self._release_dialog_slot()

    def _subscribe_event_handlers(self, event_handlers: dict[type[Any], Callable[[Any], Awaitable[None]]]) -> None:
        for event, handler in event_handlers.items():
            unsubscriber = self._event_bus.subscribe(event, handler)
            self.__add_unsubscriber(unsubscriber)

    def _subscribe_state_listeners(self, state_listeners: dict[str, Callable[[Any], None]]) -> None:
        for state, listener in state_listeners.items():
            unsubscriber = self._state_store.subscribe(state, listener)
            self.__add_unsubscriber(unsubscriber)

    async def _try_acquire_dialog_slot(self) -> bool:
        if BaseController._dialog_lock.locked():
            return False
        try:
            await asyncio.wait_for(BaseController._dialog_lock.acquire(), timeout=0.1)
        except asyncio.TimeoutError:
            return False
        dialog = getattr(self._page, "dialog", None)
        if dialog is not None and getattr(dialog, "open", True):
            if BaseController._dialog_lock.locked():
                BaseController._dialog_lock.release()
            return False
        return True

    async def _wait_for_dialog_clear(self) -> None:
        while True:
            dialog = getattr(self._page, "dialog", None)
            if dialog is None:
                return
            if not getattr(dialog, "open", True):
                return
            await asyncio.sleep(0.05)

    async def _wait_for_dialog_closed(self, dialog: Any) -> None:
        while True:
            current_dialog = getattr(self._page, "dialog", None)
            if current_dialog is not dialog:
                return
            if not getattr(dialog, "open", True):
                return
            await asyncio.sleep(0.05)

    def __add_unsubscriber(self, func: Callable[[], None]) -> None:
        self.__unsubscribers.append(func)

    async def __close_loading_after_delay(self, delay: float) -> None:
        try:
            await asyncio.sleep(max(delay, 0))
        finally:
            self.__finalize_loading_close()

    def __finalize_loading_close(self) -> None:
        if self._loading_dialog:
            self._page.pop_dialog()
        self._loading_dialog = None
        self.__loading_opened_at = None
        self.__loading_close_task = None
        if self.__loading_lock_acquired:
            self._release_dialog_slot()
            self.__loading_lock_acquired = False
