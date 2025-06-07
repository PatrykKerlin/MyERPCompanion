from __future__ import annotations
from typing import TYPE_CHECKING
from controllers.base import BaseComponentController
from services.base import BaseService
from config.views import Views
from views.components import SideMenuComponent

if TYPE_CHECKING:
    from config.context import Context


class SideMenuController(BaseComponentController[BaseService, SideMenuComponent]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__view_registry = Views()

    @property
    def component(self) -> SideMenuComponent:
        return SideMenuComponent(
            controller=self,
            texts=self._context.texts,
            modules=self._context.modules,
            user=self._context.user,
            visible=True,
        )

    def on_menu_click(self, key: str) -> None:
        if key not in self._context.active_views.keys():
            controller = self._context.controllers.get_view_controller(self.__view_registry.get(key))
            view = controller.view(key)
            self._context.active_views[key] = view
        view = self._context.active_views[key]
        tabs_bar_controller = self._context.controllers.get("tabs_bar")
        tabs_bar_controller.add_tab(key)
        app_controller = self._context.controllers.get("app")
        app_controller.render_view(view)
