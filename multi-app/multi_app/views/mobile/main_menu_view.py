from __future__ import annotations

from collections.abc import Callable

import flet as ft

from utils.enums import View
from utils.translation import Translation


class MainMenuView(ft.Container):
    def __init__(self, translation: Translation, on_view_selected: Callable[[View], None]) -> None:
        self.__translation = translation
        self.__on_view_selected = on_view_selected
        self.__menu_items: list[tuple[View, str]] = [
            (View.BINS, "bins"),
            (View.ITEMS, "items"),
            (View.BIN_TRANSFER, "bin_transfer"),
            (View.ORDER_PICKING, "order_picking"),
            (View.STOCK_RECEIVING, "stock_receiving"),
        ]
        self.__buttons: dict[View, ft.Button] = {}
        for view_key, label_key in self.__menu_items:
            self.__buttons[view_key] = ft.Button(
                content=self.__translation.get(label_key),
                expand=True,
                on_click=self.__build_on_click(view_key),
            )
        ft.Container.__init__(
            self,
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[button for button in self.__buttons.values()],
                tight=True,
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                width=320,
            ),
        )

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        for view_key, label_key in self.__menu_items:
            button = self.__buttons[view_key]
            button.content = self.__translation.get(label_key)
            if button.page:
                button.update()

    def __build_on_click(self, view_key: View) -> Callable[[ft.ControlEvent], None]:
        return lambda _: self.__on_view_selected(view_key)
