from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from flet import Control

from controllers.base.base_controller import BaseController
from services.base.base_service import BaseService

TService = TypeVar("TService", bound=BaseService)
TComponent = TypeVar("TComponent", bound=Control)


class BaseComponentController(BaseController, Generic[TService, TComponent], ABC):
    pass

    # @abstractmethod
    # def get_new_component(self) -> TComponent:
    #     pass
