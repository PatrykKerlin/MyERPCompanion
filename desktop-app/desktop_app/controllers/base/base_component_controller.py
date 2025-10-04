from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from flet import Control

from config.context import Context
from controllers.base.base_controller import BaseController
from services.base.base_service import BaseService
from events.base.base_event import BaseEvent

TComponent = TypeVar("TComponent", bound=Control)
TEvent = TypeVar("TEvent", bound=BaseEvent)


class BaseComponentController(BaseController, Generic[TComponent, TEvent], ABC):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._component: TComponent | None = None

    @abstractmethod
    async def _component_requested_handler(self, _: TEvent) -> None:
        pass
