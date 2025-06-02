from __future__ import annotations
from typing import TYPE_CHECKING

from controllers.base import BaseComponentController
from services.base import BaseService
from views.components import TabsBar

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[BaseService, TabsBar]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__tabs_bar: TabsBar | None = None
        self.__tabs: list[str] = []
        self.__active: str = ""

    @property
    def component(self) -> TabsBar:
        self.__tabs_bar = TabsBar(
            controller=self,
            texts=self._context.texts,
            tabs=self.__tabs,
            active_tab=self.__active,
        )
        return self.__tabs_bar

    def add_tab(self, key: str) -> None:
        if key not in self._context.active_views:
            return
        if key not in self.__tabs:
            self.__tabs.append(key)
        self.__active = key
        self.__refresh()

    def on_tab_open(self, key: str) -> None:
        self.__active = key
        self.__refresh()
        app_controller = self._context.controllers.get("app")
        app_controller.render_view(self._context.active_views[key])

    def on_tab_close(self, key: str) -> None:
        if key in self.__tabs:
            index = self.__tabs.index(key)
            self.__tabs.remove(key)
            self._context.active_views.pop(key, None)

            if self.__active == key:
                if self.__tabs:
                    self.__active = self.__tabs[max(index - 1, 0)]
                else:
                    self.__active = ""
            self.__refresh()

            if self.__active:
                app_controller = self._context.controllers.get("app")
                app_controller.render_view(self._context.active_views[self.__active])

    def __refresh(self) -> None:
        if self.__tabs_bar:
            self.__tabs_bar.tabs = self.__tabs
            self.__tabs_bar.active_tab = self.__active
            self.__tabs_bar.refresh()
