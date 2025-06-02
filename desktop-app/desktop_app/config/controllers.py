from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from controllers.core import AppController
from controllers.components import AuthDialogController, ButtonsBarController, SideMenuController, TabsBarController

if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController
    from context import Context

ControllerName = Literal["app", "auth_dialog", "buttons_bar", "side_menu", "tabs_bar"]


class Controllers:
    def __init__(self, context: Context) -> None:
        self.__context = context
        self.__controllers: dict[str, BaseController] = {}

    def initialize(self) -> None:
        self.__controllers["app"] = AppController(self.__context)
        self.__controllers["auth_dialog"] = AuthDialogController(self.__context)
        self.__controllers["buttons_bar"] = ButtonsBarController(self.__context)
        self.__controllers["side_menu"] = SideMenuController(self.__context)
        self.__controllers["tabs_bar"] = TabsBarController(self.__context)

    @overload
    def get(self, name: Literal["app"]) -> AppController: ...

    @overload
    def get(self, name: Literal["auth_dialog"]) -> AuthDialogController: ...

    @overload
    def get(self, name: Literal["buttons_bar"]) -> ButtonsBarController: ...

    @overload
    def get(self, name: Literal["side_menu"]) -> SideMenuController: ...

    @overload
    def get(self, name: Literal["tabs_bar"]) -> TabsBarController: ...

    def get(self, name: ControllerName) -> BaseController:
        return self.__controllers[name]
