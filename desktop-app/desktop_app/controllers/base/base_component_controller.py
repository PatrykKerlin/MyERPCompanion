from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from flet import Control

from controllers.base import BaseController
from services.base import BaseService

TService = TypeVar("TService", bound=BaseService)
TComponent = TypeVar("TComponent", bound=Control)


class BaseComponentController(BaseController, Generic[TService, TComponent], ABC):
    @abstractmethod
    def get_new_component(self) -> TComponent:
        pass
