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


class BaseComponentController(BaseController[TService], Generic[TService, TComponent], ABC):
    _service_cls: type[TService] | None = None

    @property
    @abstractmethod
    def component(self) -> TComponent:
        pass
