from __future__ import annotations
from typing import TYPE_CHECKING
from controllers.base import BaseComponentController
from services.base import BaseService
from config.views import Views
from views.components import SideMenu

if TYPE_CHECKING:
    from config.context import Context


class SideMenuController(BaseComponentController[BaseService, SideMenu]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__view_registry = Views()

    @property
    def component(self) -> SideMenu:
        return SideMenu(
            texts=self._context.texts,
            modules=self._context.modules,
            user=self._context.user,
            controller=self,
            visible=True,
        )

    def on_menu_click(self, endpoint_key: str) -> None:
        if endpoint_key not in self._context.active_views.keys():
            view_cls = self.__view_registry.get(endpoint_key)
            self._context.active_views[endpoint_key] = view_cls()
        view = self._context.active_views[endpoint_key]
        tabs_bar_controller = self._context.controllers.get("tabs_bar")
        tabs_bar_controller.add_tab(endpoint_key)
        app_controller = self._context.controllers.get("app")
        app_controller.render_view(view)
