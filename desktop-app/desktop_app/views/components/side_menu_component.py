from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import AlignmentStyles
from styles.dimensions import AppDimensions
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.components.side_menu_controller import SideMenuController
    from utils.translation import Translation


class SideMenuComponent(BaseComponent, ft.Container):
    def __init__(
        self, controller: SideMenuController, translation: Translation, content: dict[str, list[tuple[int, str]]]
    ) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__content = content
        self.__labels: list[str] = []
        self.__controls: list[ft.Control] = []
        self.__menu_column = ft.Column(
            controls=self.__controls,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=AlignmentStyles.AXIS_START,
            horizontal_alignment=AlignmentStyles.CROSS_CENTER,
        )
        self.__build_controls()
        ft.Container.__init__(
            self,
            content=self.__menu_column,
            alignment=AlignmentStyles.TOP_CENTER,
            width=self.__calculate_width(),
            opacity=1.0,
            animate=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_opacity=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_size=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
        )

    def set_scroll_enabled(self, enabled: bool) -> None:
        self.__menu_column.scroll = ft.ScrollMode.ADAPTIVE if enabled else ft.ScrollMode.HIDDEN

    def __build_controls(self) -> None:
        for module_key, view_params in self.__content.items():
            module_label = self._translation.get(module_key)
            self.__labels.append(module_label)
            self.__controls.append(ft.Text(value=module_label))
            for module_id, view_key in view_params:
                view_label = self._translation.get(view_key)
                self.__labels.append(view_label)
                self.__controls.append(
                    ft.ListTile(
                        title=ft.Text(view_label),
                        leading=ft.Icon(icon=ft.Icons.VIEW_LIST),
                        dense=True,
                        on_click=lambda _, id=module_id, key=view_key: self._controller.on_item_clicked(id, key),
                    )
                )

    def __calculate_width(self) -> int:
        max_length = max((len(label) for label in self.__labels), default=20)
        preferred = max_length * AppDimensions.SIDE_MENU_CHAR_WIDTH + AppDimensions.SIDE_MENU_EXTRA_WIDTH
        return max(AppDimensions.SIDE_MENU_MIN_WIDTH, min(preferred, AppDimensions.SIDE_MENU_MAX_WIDTH))
