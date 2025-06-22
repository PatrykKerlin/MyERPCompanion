from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base import BaseComponentController
from services.base import BaseService
from views.components import TabsBarComponent

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[BaseService, TabsBarComponent]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__active_view_key: str = ""
        self.__tabs: list[str] = []
        self.__tabs_bar: TabsBarComponent | None = None

    @property
    def active_view_key(self) -> str:
        return self.__active_view_key

    def get_new_component(self) -> TabsBarComponent:
        self.__tabs_bar = TabsBarComponent(
            controller=self,
            texts=self._context.texts,
            tabs=self.__tabs,
            active_tab=self.__active_view_key,
        )
        return self.__tabs_bar

    def add_tab(self, key: str) -> None:
        if key not in self._context.active_views:
            return
        if key not in self.__tabs:
            self.__tabs.append(key)
            self._context.active_views[key].visible = True
        self.on_tab_open(key)

    def on_tab_open(self, key: str) -> None:
        self.__active_view_key = key
        self.__refresh()
        for key, view in self._context.active_views.items():
            view.set_visible(key == self.__active_view_key)
        active_view = self._context.active_views[self.__active_view_key]
        view_controller = self._context.controllers.get_view_controller(active_view.controller_key)
        view_controller.set_view(active_view)
        self._context.controllers.get("toolbar").refresh()
        self._context.page.update()

    def on_tab_close(self, key: str | None = None) -> None:
        if key and key not in self.__tabs:
            return
        if not key:
            key = self.__active_view_key
        self.__tabs.remove(key)
        old_view = self._context.active_views.pop(key, None)
        if old_view:
            view_controller = self._context.controllers.get_view_controller(old_view.controller_key)
            view_controller.set_view(None)
            view_stack = self._context.controllers.get("app").view_stack
            self._remove_control(view_stack, old_view)
        if self.__tabs:
            self.__active_view_key = self.__tabs[-1]
            new_view = self._context.active_views[self.__active_view_key]
            new_view_controller = self._context.controllers.get_view_controller(new_view.controller_key)
            new_view_controller.set_view(new_view)
        else:
            self.__active_view_key = ""
        self.__refresh()
        for key, view in self._context.active_views.items():
            view.set_visible(key == self.__active_view_key)
        self._context.controllers.get("toolbar").refresh()
        self._context.page.update()

    def __refresh(self) -> None:
        if self.__tabs_bar:
            self.__tabs_bar.tabs = self.__tabs
            self.__tabs_bar.active_tab = self.__active_view_key
            self.__tabs_bar.refresh()
