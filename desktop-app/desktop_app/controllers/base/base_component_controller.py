from abc import ABC, abstractmethod
from typing import Generic, TypeVar, TYPE_CHECKING

from flet import Control

from controllers.base import BaseController
from services.base import BaseService

if TYPE_CHECKING:
    from config.context import Context


TService = TypeVar("TService", bound=BaseService)
TComponent = TypeVar("TComponent", bound=Control)


class BaseComponentController(BaseController, Generic[TService, TComponent], ABC):
    @abstractmethod
    def get_new_component(self) -> TComponent:
        pass
