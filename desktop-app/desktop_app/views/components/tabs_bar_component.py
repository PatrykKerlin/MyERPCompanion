from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions
from styles.styles import ButtonStyles
from utils.enums import ViewMode
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.components.tabs_bar_controller import TabsBarController
    from utils.translation import Translation


class TabsBarComponent(BaseComponent, ft.Container):
    def __init__(self, controller: TabsBarController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        ft.Container.__init__(
            self,
            padding=ft.Padding.symmetric(horizontal=AppDimensions.TABS_BAR_EDGE_PADDING),
        )
        self.__tabs: list[str] = []
        self.__active_tab = ""
        self.__active_mode = ViewMode.READ
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

    @property
    def active_mode(self) -> ViewMode:
        return self.__active_mode

    @active_mode.setter
    def active_mode(self, active_mode: ViewMode) -> None:
        self.__active_mode = active_mode

    def refresh(self) -> None:
        self.__build_controls()
        self.safe_update(self)

    def __build_controls(self) -> None:
        controls: list[ft.Control] = []
        active_border_color = self.__resolve_active_border_color(self.__active_mode)
        for title in self.__tabs:
            is_active = title == self.__active_tab
            tab_border_color = active_border_color if is_active else AppColors.OUTLINE
            tab_container = ft.Container(
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
                border_radius=ft.BorderRadius.only(
                    top_left=AppDimensions.RADIUS_MD,
                    top_right=AppDimensions.RADIUS_MD,
                    bottom_left=0,
                    bottom_right=0,
                ),
                border=ft.Border.all(AppDimensions.TAB_CARD_BORDER_WIDTH, tab_border_color),
                padding=ft.Padding.only(
                    left=AppDimensions.SPACE_2XS,
                    right=AppDimensions.SPACE_2XS,
                    top=AppDimensions.SPACE_2XS,
                    bottom=0,
                ),
                alignment=ft.Alignment.CENTER_LEFT,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
                ink=False,
                on_click=lambda _, title=title: self._controller.on_tab_clicked(title),
            )
            if is_active:
                controls.append(
                    ft.Stack(
                        controls=[
                            tab_container,
                            ft.Container(
                                left=0,
                                right=0,
                                bottom=-AppDimensions.TAB_CARD_BORDER_WIDTH,
                                height=AppDimensions.TAB_CARD_BORDER_WIDTH * 2,
                                bgcolor=AppColors.CARD,
                                ignore_interactions=True,
                            ),
                        ],
                        fit=ft.StackFit.LOOSE,
                    )
                )
            else:
                controls.append(
                    ft.Stack(
                        controls=[
                            tab_container,
                            ft.Container(
                                left=0,
                                right=0,
                                bottom=0,
                                height=AppDimensions.TAB_CARD_BORDER_WIDTH,
                                bgcolor=active_border_color,
                                ignore_interactions=True,
                            ),
                        ],
                        fit=ft.StackFit.LOOSE,
                    )
                )
        cast(ft.Row, self.content).controls = cast(list[ft.Control], controls)

    @staticmethod
    def __resolve_active_border_color(mode: ViewMode) -> ft.ColorValue:
        if mode in (ViewMode.CREATE, ViewMode.EDIT):
            return AppColors.ACTIVE_BORDER_RED
        return AppColors.OUTLINE
