from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.base import BaseController


class Controllers:
    def __init__(self) -> None:
        self.__controllers: dict[str, BaseController] = {}

    def __getattr__(self, name: str) -> BaseController:
        try:
            return self.__controllers[name]
        except KeyError:
            raise AttributeError(f"Controller '{name}' is not registered.")

    def add(self, name: str, controller: BaseController) -> None:
        self.__controllers[name] = controller
