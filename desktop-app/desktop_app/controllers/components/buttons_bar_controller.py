from __future__ import annotations
from typing import TYPE_CHECKING, cast
import flet as ft

from controllers.base import BaseComponentController
from services.base import BaseService
from views.components import ButtonsBarComponent, SideMenuComponent

if TYPE_CHECKING:
    from config.context import Context


class ButtonsBarController(BaseComponentController[BaseService, ButtonsBarComponent]):
    def __init__(self, context: Context):
        super().__init__(context)
        self.__side_menu_visible = True

    @property
    def component(self) -> ButtonsBarComponent:
        return ButtonsBarComponent(self, texts=self._context.texts)

    def toggle_side_menu(self) -> None:
        side_menu = self.__get_side_menu()
        if not side_menu:
            return
        self.__side_menu_visible = not self.__side_menu_visible
        side_menu.width = side_menu.calculated_width if self.__side_menu_visible else 0
        side_menu.opacity = 1.0 if self.__side_menu_visible else 0.0
        self._context.page.update()

    def __get_side_menu(self) -> SideMenuComponent | None:
        column = self._context.page.controls[0] if self._context.page.controls else []
        column = cast(ft.Column, column)
        row = column.controls[4]
        row = cast(ft.Row, row)
        return row.controls[0] if isinstance(row.controls[0], SideMenuComponent) else None
