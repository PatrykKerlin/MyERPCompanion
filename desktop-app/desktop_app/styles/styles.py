import flet as ft


class ButtonStyles:
    small_padding = ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=20, vertical=10))


class MenuStyles:
    flat = ft.MenuStyle(
        elevation=0,
        bgcolor=ft.Colors.SURFACE,
        alignment=ft.alignment.top_left,
    )
