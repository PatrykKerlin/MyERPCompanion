from __future__ import annotations


import asyncio
from typing import Awaitable, Callable, TypeVar, Any


from events.events import BaseEvent

TEvent = TypeVar("TEvent", bound=BaseEvent)


class EventBus:
    def __init__(self) -> None:
        self.__subscriptions: dict[type[BaseEvent], list[Callable[[Any], Awaitable[None]]]] = {}
        self.__queue: asyncio.Queue[BaseEvent] = asyncio.Queue()
        self.__task: asyncio.Task[None] | None = None

    def subscribe(self, event: type[BaseEvent], handler: Callable[[TEvent], Awaitable[None]]) -> Callable[[], None]:
        def unsubscribe() -> None:
            handlers = self.__subscriptions.get(event, [])
            if handler in handlers:
                handlers.remove(handler)
            if not handlers and event in self.__subscriptions:
                del self.__subscriptions[event]

        self.__subscriptions.setdefault(event, []).append(handler)

        return unsubscribe

    async def publish(self, event: BaseEvent) -> None:
        await self.__queue.put(event)

    def start(self) -> None:
        if self.__task is None or self.__task.done():
            self.__task = asyncio.create_task(self.__run())

    async def stop(self) -> None:
        if self.__task and not self.__task.done():
            self.__task.cancel()
            try:
                await self.__task
            except asyncio.CancelledError:
                pass
            self.__task = None
        self.__subscriptions.clear()
        while not self.__queue.empty():
            try:
                self.__queue.get_nowait()
                self.__queue.task_done()
            except asyncio.QueueEmpty:
                break

    async def __run(self) -> None:
        while True:
            event = await self.__queue.get()
            try:
                handlers = list(self.__subscriptions.get(type(event), []))
                for handler in handlers:
                    await handler(event)
            finally:
                self.__queue.task_done()
