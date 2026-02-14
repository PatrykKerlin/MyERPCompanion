import flet as ft
from styles.colors import AppColors


class ButtonStyles:
    small_padding = ft.ButtonStyle(padding=ft.Padding.symmetric(horizontal=20, vertical=10))


class MenuStyles:
    flat = ft.MenuStyle(
        elevation=0,
        bgcolor=AppColors.SURFACE,
        alignment=ft.Alignment.TOP_LEFT,
    )
