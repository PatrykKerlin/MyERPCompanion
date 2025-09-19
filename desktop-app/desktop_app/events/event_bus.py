from __future__ import annotations


import asyncio
from typing import Awaitable, Callable


from events.types import BaseEvent


class EventBus:
    def __init__(self) -> None:
        self.__subscriptions: dict[str, list[Callable[[BaseEvent], Awaitable[None]]]] = {}
        self.__queue: asyncio.Queue[BaseEvent] = asyncio.Queue()
        self.__task: asyncio.Task[None] | None = None

    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> Callable[[], None]:
        def unsubscribe() -> None:
            handlers = self.__subscriptions.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)
            if not handlers and event_type in self.__subscriptions:
                del self.__subscriptions[event_type]

        self.__subscriptions.setdefault(event_type, []).append(handler)

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
                handlers = list(self.__subscriptions.get(event.type(), []))
                for handler in handlers:
                    await handler(event)
            finally:
                self.__queue.task_done()
