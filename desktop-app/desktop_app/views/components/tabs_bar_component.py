from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft

from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.tabs_bar_controller import TabsBarController


class TabsBarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: TabsBarController, texts: dict[str, str], tabs: list[str], active_tab: str) -> None:
        BaseComponent.__init__(self, controller, texts)
        ft.Container.__init__(self)
        self.__tabs = tabs
        self.__active_tab = active_tab
        self.content = ft.Row(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self._controller = controller
        self.__build_controls()

    @property
    def tabs(self) -> list[str]:
        return self.__tabs

    @tabs.setter
    def tabs(self, tabs: list[str]) -> None:
        self.__tabs = tabs

    @property
    def active_tab(self) -> str:
        return self.__active_tab

    @active_tab.setter
    def active_tab(self, active_tab: str) -> None:
        self.__active_tab = active_tab

    def __build_controls(self) -> None:
        controls = [
            ft.Row(
                controls=[
                    ft.TextButton(
                        text=self._texts[key],
                        on_click=lambda _, key=key: self._controller.on_tab_open(key),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda _, key=key: self._controller.on_tab_close(key),
                        expand=True,
                    ),
                ]
            )
            for key in self.__tabs
        ]
        cast(ft.Row, self.content).controls = controls

    def refresh(self) -> None:
        self.__build_controls()
        self.update()
