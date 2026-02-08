from __future__ import annotations

from collections.abc import Callable

import flet as ft

from utils.translation import Translation


class BinsView(ft.Container):
    def __init__(self, translation: Translation, on_back: Callable[[], None]) -> None:
        self.__translation = translation
        self.__on_back = on_back
        self.__title = ft.Text(
            self.__translation.get("bins"),
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        self.__placeholder = ft.Text(
            self.__translation.get("mobile_bins_placeholder"),
            text_align=ft.TextAlign.CENTER,
        )
        self.__back_button = ft.Button(
            content=self.__translation.get("back_to_menu"),
            on_click=self.__on_back_click,
            width=220,
        )
        ft.Container.__init__(
            self,
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(horizontal=16, vertical=20),
            content=ft.Column(
                controls=[
                    self.__title,
                    self.__placeholder,
                    ft.Container(height=16),
                    self.__back_button,
                ],
                tight=True,
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title.value = self.__translation.get("bins")
        self.__placeholder.value = self.__translation.get("mobile_bins_placeholder")
        self.__back_button.content = self.__translation.get("back_to_menu")
        if self.page:
            self.update()

    def __on_back_click(self, _: ft.ControlEvent) -> None:
        self.__on_back()
