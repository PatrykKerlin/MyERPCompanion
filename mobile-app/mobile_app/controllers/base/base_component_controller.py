from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from config.context import Context
from controllers.base.base_controller import BaseController
from events.base.base_event import BaseEvent
from flet import Control
from utils.enums import Module

TComponent = TypeVar("TComponent", bound=Control)
TEvent = TypeVar("TEvent", bound=BaseEvent)


class BaseComponentController(BaseController, Generic[TComponent, TEvent], ABC):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._component: TComponent | None = None
        self._module_id = Module.CORE

    @abstractmethod
    async def _component_requested_handler(self, _: TEvent) -> None:
        pass
