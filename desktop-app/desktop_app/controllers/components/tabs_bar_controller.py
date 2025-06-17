from __future__ import annotations
from typing import TYPE_CHECKING, cast

import flet as ft

from controllers.base import BaseComponentController
from services.base import BaseService
from views.components import TabsBarComponent

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[BaseService, TabsBarComponent]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.active_view_key: str = ""
        self.__tabs_bar: TabsBarComponent | None = None
        self.__tabs: list[str] = []

    @property
    def component(self) -> TabsBarComponent:
        self.__tabs_bar = TabsBarComponent(
            controller=self,
            texts=self._context.texts,
            tabs=self.__tabs,
            active_tab=self.active_view_key,
        )
        return self.__tabs_bar

    def add_tab(self, key: str) -> None:
        if key not in self._context.active_views:
            return
        if key not in self.__tabs:
            self.__tabs.append(key)
            self._context.active_views[key].visible = True
        self._context.controllers.get("buttons_bar").set_lock_view_button_disabled(False)
        self.on_tab_open(key)

    def on_tab_open(self, key: str) -> None:
        self.active_view_key = key
        self.__refresh()
        for key, view in self._context.active_views.items():
            view.set_visible(key == self.active_view_key)
        self._context.page.update()

    def on_tab_close(self, key: str) -> None:
        if key not in self.__tabs:
            return
        self.__tabs.remove(key)
        view = self._context.active_views.pop(key, None)
        if view and self._context.page.controls:
            outer_column = cast(ft.Column, self._context.page.controls[0])
            row = cast(ft.Row, outer_column.controls[4])
            inner_column = cast(ft.Column, row.controls[1])
            stack = inner_column.controls[1]
            self._remove_control(stack, view)
        if self.__tabs:
            self.active_view_key = self.__tabs[-1]
        else:
            self.active_view_key = ""
        self.__refresh()
        for key, view in self._context.active_views.items():
            view.set_visible(key == self.active_view_key)
        self._context.page.update()

    def __refresh(self) -> None:
        if self.__tabs_bar:
            self.__tabs_bar.tabs = self.__tabs
            self.__tabs_bar.active_tab = self.active_view_key
            self.__tabs_bar.refresh()
