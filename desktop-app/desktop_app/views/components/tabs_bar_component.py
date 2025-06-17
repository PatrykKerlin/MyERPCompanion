from __future__ import annotations
from typing import cast, TYPE_CHECKING
import flet as ft
from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.components.tabs_bar_controller import TabsBarController


class TabsBarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: TabsBarController, texts: dict[str, str], tabs: list[str], active_tab: str) -> None:
        BaseComponent.__init__(self, controller, texts)
        ft.Container.__init__(self)
        self.tabs = tabs
        self.active_tab = active_tab
        self.content = ft.Row(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self._controller = controller
        self.__build_controls()

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
            for key in self.tabs
        ]
        cast(ft.Row, self.content).controls = controls

    def refresh(self) -> None:
        self.__build_controls()
        self.update()
