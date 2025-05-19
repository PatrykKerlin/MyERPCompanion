from flet import Page
from collections.abc import Callable, Awaitable
from typing import Any


class SafeExecutor:
    def __init__(self, page: Page) -> None:
        self._page = page

    def run_ui(
        self, sync_func: Callable[..., None], sync_args: list[Any] = [], sync_kwargs: dict[str, Any] = {}
    ) -> None:
        lambda_func = lambda: sync_func(*sync_args, **sync_kwargs)
        self._page.loop.call_soon_threadsafe(lambda_func)

    def run_async(
        self, async_func: Callable[..., Awaitable[Any]], async_args: list[Any] = [], async_kwargs: dict[str, Any] = {}
    ) -> None:
        async def wrapper() -> None:
            await async_func(*async_args, **async_kwargs)

        self._page.run_task(wrapper)

    def run_async_with_ui_callback(
        self,
        async_func: Callable[..., Awaitable[Any]],
        async_args: list[Any] = [],
        async_kwargs: dict[str, Any] = {},
        sync_func: Callable[..., None] = lambda: None,
        sync_args: list[Any] = [],
        sync_kwargs: dict[str, Any] = {},
    ) -> None:
        async def wrapper() -> None:
            await async_func(*async_args, **async_kwargs)
            self.run_ui(sync_func, sync_args, sync_kwargs)

        self._page.run_task(wrapper)
