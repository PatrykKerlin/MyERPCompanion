import asyncio
from logging import Logger
from threading import RLock
from typing import Any, Awaitable, Callable, TypeVar

from events.events import BaseEvent

TEvent = TypeVar("TEvent", bound=BaseEvent)


class EventBus:
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger
        self.__subscriptions: dict[type[BaseEvent], list[Callable[[Any], Awaitable[None]]]] = {}
        self.__event_queue: asyncio.Queue[BaseEvent] = asyncio.Queue()
        self.__handler_queue: asyncio.Queue[tuple[Callable[[Any], Awaitable[None]], BaseEvent]] = asyncio.Queue()
        self.__event_workers: list[asyncio.Task[None]] = []
        self.__handler_workers: list[asyncio.Task[None]] = []
        self.__event_workers_qty = 4
        self.__handler_workers_qty = 8
        self.__started = False
        self.__subs_lock = RLock()

    def subscribe(self, event: type[BaseEvent], handler: Callable[[TEvent], Awaitable[None]]) -> Callable[[], None]:
        with self.__subs_lock:
            self.__subscriptions.setdefault(event, []).append(handler)

        def unsubscribe() -> None:
            with self.__subs_lock:
                handlers = self.__subscriptions.get(event, [])
                if handler in handlers:
                    handlers.remove(handler)
                if not handlers and event in self.__subscriptions:
                    del self.__subscriptions[event]

        return unsubscribe

    async def publish(self, event: BaseEvent) -> None:
        await self.__event_queue.put(event)

    def start(self) -> None:
        if self.__started:
            return
        self.__started = True
        for _ in range(self.__event_workers_qty):
            self.__event_workers.append(asyncio.create_task(self.__run_event_worker()))
        for _ in range(self.__handler_workers_qty):
            self.__handler_workers.append(asyncio.create_task(self.__run_handler_worker()))

    async def stop(self) -> None:
        if not self.__started:
            return
        self.__started = False
        for task in self.__event_workers + self.__handler_workers:
            task.cancel()
        for task in self.__event_workers + self.__handler_workers:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self.__event_workers.clear()
        self.__handler_workers.clear()
        with self.__subs_lock:
            self.__subscriptions.clear()
        while not self.__event_queue.empty():
            try:
                self.__event_queue.get_nowait()
                self.__event_queue.task_done()
            except asyncio.QueueEmpty:
                break
        while not self.__handler_queue.empty():
            try:
                self.__handler_queue.get_nowait()
                self.__handler_queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def __run_event_worker(self) -> None:
        while True:
            try:
                event = await self.__event_queue.get()
            except asyncio.CancelledError:
                break
            try:
                with self.__subs_lock:
                    handlers = list(self.__subscriptions.get(type(event), []))
                for handler in handlers:
                    await self.__handler_queue.put((handler, event))
            finally:
                self.__event_queue.task_done()

    async def __run_handler_worker(self) -> None:
        while True:
            try:
                handler, event = await self.__handler_queue.get()
            except asyncio.CancelledError:
                break
            try:
                result = await handler(event)
                if isinstance(result, Exception):
                    self.__logger.error(f"Error while handling {type(event).__name__}: {result}", exc_info=True)
            except Exception as err:
                self.__logger.error(f"Error while handling {type(event).__name__}: {err}", exc_info=True)
            finally:
                self.__handler_queue.task_done()
