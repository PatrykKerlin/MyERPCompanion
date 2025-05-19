from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controllers.base import BaseController
    from ..services.base import BaseService


class Controllers:
    def __init__(self) -> None:
        self.__controllers: dict[str, BaseController[BaseService]] = {}

    def __getattr__(self, name: str) -> BaseController[BaseService]:
        try:
            return self.__controllers[name]
        except KeyError:
            raise AttributeError(f"Controller '{name}' is not registered.")

    def add(self, name: str, controller: BaseController[BaseService]) -> None:
        self.__controllers[name] = controller
