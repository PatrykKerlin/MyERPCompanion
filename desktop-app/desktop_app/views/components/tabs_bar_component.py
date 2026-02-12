from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.components.tabs_bar_controller import TabsBarController
    from utils.translation import Translation


class TabsBarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: TabsBarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        ft.Container.__init__(self)
        self.__tabs: list[str] = []
        self.__active_tab = ""
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

    def refresh(self) -> None:
        self.__build_controls()
        self.update()

    def __build_controls(self) -> None:
        controls = [
            ft.Row(
                controls=[
                    ft.TextButton(
                        content=title,
                        on_click=lambda _, title=title: self._controller.on_tab_clicked(title),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda _, title=title: self._controller.on_close_clicked(title),
                        expand=True,
                    ),
                ]
            )
            for title in self.__tabs
        ]
        cast(ft.Row, self.content).controls = cast(list[ft.Control], controls)
