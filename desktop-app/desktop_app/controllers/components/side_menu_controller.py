from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base import BaseComponentController
from services.base import BaseService
from views.components import SideMenuComponent

if TYPE_CHECKING:
    from config.context import Context


class SideMenuController(BaseComponentController[BaseService, SideMenuComponent]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__content: dict[str, list[str]] = {}
        self.__side_menu: SideMenuComponent | None = None

    @property
    def side_menu(self) -> SideMenuComponent | None:
        return self.__side_menu

    def get_new_component(self) -> SideMenuComponent:
        self.__side_menu = SideMenuComponent(
            controller=self,
            texts=self._context.texts,
            content=self.__content,
        )
        return self.__side_menu

    def set_content(self, content: dict[str, list[str]]) -> None:
        self.__content = content

    def on_menu_click(self, key: str) -> None:
        if key not in self._context.active_views.keys():
            controller = self._context.controllers.get_view_controller(key)
            view = controller.get_new_view()
            self._context.active_views[key] = view
        view = self._context.active_views[key]
        self._context.controllers.get("tabs_bar").add_tab(key)
        self._context.controllers.get("app").render_view(view)
        self._context.controllers.get("toolbar").refresh()
