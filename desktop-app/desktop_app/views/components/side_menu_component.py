from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from utils.translation import Translation
    from controllers.components.side_menu_controller import SideMenuController


class SideMenuComponent(BaseComponent, ft.Container):
    def __init__(self, controller: SideMenuController, translation: Translation, content: dict[str, list[str]]) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__content = content
        self.__labels: list[str] = []
        self.__controls: list[ft.Control] = []
        self.__build_controls()
        ft.Container.__init__(
            self,
            content=ft.Column(
                controls=self.__controls,
                expand=True,
                scroll=ft.ScrollMode.ADAPTIVE,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.top_center,
            width=self.__calculate_width(),
            opacity=1.0,
            animate_opacity=300,
            animate_size=300,
        )

    def __build_controls(self) -> None:
        for module_key, view_keys in self.__content.items():
            module_label = self._translation.get(module_key)
            self.__labels.append(module_label)
            self.__controls.append(ft.Text(value=module_label))
            for view_key in view_keys:
                view_label = self._translation.get(view_key)
                self.__labels.append(view_label)
                self.__controls.append(
                    ft.ListTile(
                        title=ft.Text(view_label),
                        leading=ft.Icon(name=ft.Icons.VIEW_LIST),
                        dense=True,
                        on_click=lambda _, key=view_key: self._controller.on_item_clicked(key),
                    )
                )

    def __calculate_width(self) -> int:
        max_length = max((len(label) for label in self.__labels), default=20)
        return max_length * 10 + 40
