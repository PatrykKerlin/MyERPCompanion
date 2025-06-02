from __future__ import annotations
from typing import cast, TYPE_CHECKING
import flet as ft

if TYPE_CHECKING:
    from controllers.components.tabs_bar_controller import TabsBarController


class TabsBar(ft.Container):
    def __init__(self, controller: TabsBarController, texts: dict[str, str], tabs: list[str], active_tab: str) -> None:
        super().__init__()
        self.tabs = tabs
        self.active_tab = active_tab
        self.content = ft.Row(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.__controller = controller
        self.__build_controls()

    def __build_controls(self) -> None:
        controls = [
            ft.Row(
                controls=[
                    ft.TextButton(
                        text=tab,
                        on_click=lambda _, tab=tab: self.__controller.on_tab_open(tab),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda _, tab=tab: self.__controller.on_tab_close(tab),
                        expand=True,
                    ),
                ]
            )
            for tab in self.tabs
        ]
        cast(ft.Row, self.content).controls = controls

    def refresh(self) -> None:
        self.__build_controls()
        self.update()
