from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles
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
            spacing=AppDimensions.SPACE_2XS,
            vertical_alignment=ft.CrossAxisAlignment.END,
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
        controls: list[ft.Control] = []
        for title in self.__tabs:
            is_active = title == self.__active_tab
            controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    title,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    no_wrap=True,
                                ),
                                padding=ft.Padding.only(left=AppDimensions.SPACE_MD),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda _, title=title: self._controller.on_close_clicked(title),
                                style=ButtonStyles.icon,
                            ),
                        ],
                        spacing=AppDimensions.SPACE_2XS,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=AppColors.CARD if is_active else None,
                    border_radius=AppDimensions.RADIUS_MD,
                    padding=ft.Padding.only(
                        left=AppDimensions.SPACE_2XS,
                        right=AppDimensions.SPACE_2XS,
                        top=AppDimensions.SPACE_2XS,
                        bottom=0,
                    ),
                    alignment=ft.Alignment.CENTER_LEFT,
                    ink=False,
                    on_click=lambda _, title=title: self._controller.on_tab_clicked(title),
                )
            )
        cast(ft.Row, self.content).controls = cast(list[ft.Control], controls)
