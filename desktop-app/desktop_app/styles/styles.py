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


class AlignmentStyles:
    CENTER = ft.Alignment.CENTER
    CENTER_LEFT = ft.Alignment.CENTER_LEFT
    TOP_LEFT = ft.Alignment.TOP_LEFT
    TOP_CENTER = ft.Alignment.TOP_CENTER

    AXIS_START = ft.MainAxisAlignment.START
    AXIS_END = ft.MainAxisAlignment.END
    AXIS_CENTER = ft.MainAxisAlignment.CENTER
    AXIS_SPACE_BETWEEN = ft.MainAxisAlignment.SPACE_BETWEEN

    CROSS_START = ft.CrossAxisAlignment.START
    CROSS_CENTER = ft.CrossAxisAlignment.CENTER
    CROSS_STRETCH = ft.CrossAxisAlignment.STRETCH


class ControlStyles:
    INPUT_ALIGNMENT = AlignmentStyles.CENTER_LEFT
    LABEL_ALIGNMENT = AlignmentStyles.TOP_LEFT
    MARKER_ALIGNMENT = AlignmentStyles.TOP_LEFT
    FIELD_BORDER_RADIUS = AppDimensions.RADIUS_MD
    FIELD_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    FIELD_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY
    FIELD_BORDER = ft.Border.all(1, AppColors.OUTLINE)
    FIELD_BORDER_SIDE = ft.BorderSide(width=1, color=AppColors.OUTLINE)
    TEXT_FIELD_HEIGHT = AppDimensions.CONTROL_HEIGHT
    FIELD_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )
    DISABLED_CONTENT_OPACITY = 0.5


class MenuStyles:
    flat = ft.MenuStyle(
        elevation=0,
        bgcolor=AppColors.SURFACE,
        alignment=AlignmentStyles.TOP_LEFT,
    )
