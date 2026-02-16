import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions


class ButtonStyles:
    regular = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL,
        ),
        bgcolor=AppColors.SURFACE_CONTAINER_HIGH,
        color=AppColors.ON_SURFACE,
        side=ft.BorderSide(width=1, color=AppColors.OUTLINE),
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    compact = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL_COMPACT,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL_COMPACT,
        ),
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    icon = ft.ButtonStyle(
        padding=ft.Padding.all(0),
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    primary_regular = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL,
        ),
        bgcolor=AppColors.MATERIAL_BLUE,
        color=AppColors.ON_MATERIAL_BLUE,
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    primary_compact = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL_COMPACT,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL_COMPACT,
        ),
        bgcolor=AppColors.MATERIAL_BLUE,
        color=AppColors.ON_MATERIAL_BLUE,
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )


class ControlStyles:
    TEXT_FIELD_BORDER_RADIUS = AppDimensions.RADIUS_MD
    TEXT_FIELD_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    TEXT_FIELD_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY
    TEXT_FIELD_HEIGHT = AppDimensions.CONTROL_HEIGHT
    TEXT_FIELD_PADDING_SINGLE = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )
    TEXT_FIELD_PADDING_MULTILINE = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )

    DROPDOWN_BORDER_RADIUS = AppDimensions.RADIUS_MD
    DROPDOWN_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    DROPDOWN_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY
    DROPDOWN_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )


class MenuStyles:
    flat = ft.MenuStyle(
        elevation=0,
        bgcolor=AppColors.SURFACE,
        alignment=ft.Alignment.TOP_LEFT,
    )
