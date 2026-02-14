import flet as ft

from styles.colors import AppColors
from styles.dimensions import AppDimensions


class ComponentStyles:
    @staticmethod
    def outlined_container(expand: bool = True) -> ft.Container:
        return ft.Container(
            expand=expand,
            border=ft.Border.all(1, AppColors.OUTLINE),
            border_radius=AppDimensions.BULK_TRANSFER_BORDER_RADIUS,
            padding=AppDimensions.BULK_TRANSFER_PADDING,
        )
