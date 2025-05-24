import flet as ft
from collections.abc import Callable
from styles import MenuStyles


class IconsBar(ft.MenuBar):
    def __init__(self, texts: dict[str, str], on_menu_click: Callable[[], None]) -> None:
        super().__init__(
            style=MenuStyles.flat,
            controls=[
                ft.MenuItemButton(
                    leading=ft.Icon(ft.Icons.MENU),
                    tooltip=texts["menu"],
                    on_click=lambda _: on_menu_click(),
                ),
            ],
        )
