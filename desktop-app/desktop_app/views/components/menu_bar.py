import flet as ft

from styles import MenuStyles


class MenuBar(ft.MenuBar):
    def __init__(self, texts: dict[str, str]) -> None:
        super().__init__(
            style=MenuStyles.flat,
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(texts["file"]),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(texts["new"])),
                        ft.MenuItemButton(content=ft.Text(texts["open"])),
                        ft.MenuItemButton(content=ft.Text(texts["exit"])),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(texts["edit"]),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(texts["undo"])),
                        ft.MenuItemButton(content=ft.Text(texts["redo"])),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(texts["help"]),
                    controls=[
                        ft.MenuItemButton(content=ft.Text(texts["about"])),
                    ],
                ),
            ],
        )
