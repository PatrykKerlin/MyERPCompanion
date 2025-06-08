from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload, cast

from controllers.core import AppController, GroupController
from controllers.base import BaseViewController
from controllers.components import (
    AuthDialogController,
    ButtonsBarController,
    SideMenuController,
    TabsBarController,
    FooterBarController,
)

if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController
    from context import Context
    from schemas.core.endpoint_schema import EndpointInputSchema

ControllerName = Literal["app", "auth_dialog", "buttons_bar", "footer_bar", "side_menu", "tabs_bar", "groups"]


class Controllers:
    def __init__(self, context: Context) -> None:
        self.__context = context
        self.__controllers: dict[str, BaseController] = {}

    def initialize_window_controllers(self) -> None:
        self.__controllers["app"] = AppController(self.__context)
        self.__controllers["auth_dialog"] = AuthDialogController(self.__context)
        self.__controllers["buttons_bar"] = ButtonsBarController(self.__context)
        self.__controllers["footer_bar"] = FooterBarController(self.__context)
        self.__controllers["side_menu"] = SideMenuController(self.__context)
        self.__controllers["tabs_bar"] = TabsBarController(self.__context)

    def initialize_view_controllers(self, endpoints: dict[str, EndpointInputSchema]) -> None:
        if "groups" in endpoints.keys():
            self.__controllers["groups"] = GroupController(self.__context, endpoints["groups"])

    @overload
    def get(self, name: Literal["app"]) -> AppController: ...

    @overload
    def get(self, name: Literal["auth_dialog"]) -> AuthDialogController: ...

    @overload
    def get(self, name: Literal["buttons_bar"]) -> ButtonsBarController: ...

    @overload
    def get(self, name: Literal["footer_bar"]) -> FooterBarController: ...

    @overload
    def get(self, name: Literal["side_menu"]) -> SideMenuController: ...

    @overload
    def get(self, name: Literal["tabs_bar"]) -> TabsBarController: ...

    @overload
    def get(self, name: Literal["groups"]) -> GroupController: ...

    def get(self, name: ControllerName) -> BaseController:
        return self.__controllers[name]

    def get_view_controller(self, name: str) -> BaseViewController:
        return cast(BaseViewController, self.__controllers[name])
