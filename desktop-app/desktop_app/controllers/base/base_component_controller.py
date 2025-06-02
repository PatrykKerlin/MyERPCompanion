from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from typing import Generic, TypeVar

from flet import Control

from controllers.base import BaseController
from services.base import BaseService

if TYPE_CHECKING:
    from config.context import Context

TService = TypeVar("TService", bound=BaseService)
TComponent = TypeVar("TComponent", bound=Control)


class BaseComponentController(ABC, BaseController, Generic[TService, TComponent]):
    _service_cls: type[TService] | None = None

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        if self._service_cls:
            self._service = self._service_cls(context)

    @property
    @abstractmethod
    def component(self) -> TComponent:
        pass
