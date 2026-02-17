import math

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
    toolbar_user = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL_COMPACT,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL_COMPACT,
        ),
        color=AppColors.ON_SURFACE,
        icon_color=AppColors.ON_SURFACE,
        icon_size=AppDimensions.TOOLBAR_USER_ICON_SIZE,
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
    CENTER_RIGHT = ft.Alignment.CENTER_RIGHT
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
    INPUT_FONT_SIZE = 14
    INPUT_FONT_LINE_HEIGHT = 1.2
    INPUT_TEXT_STYLE = ft.TextStyle(size=INPUT_FONT_SIZE, height=INPUT_FONT_LINE_HEIGHT)
    FIELD_BORDER_RADIUS = AppDimensions.RADIUS_MD
    FIELD_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    FIELD_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY
    FIELD_BORDER = ft.Border.all(1, AppColors.OUTLINE)
    FIELD_BORDER_SIDE = ft.BorderSide(width=1.25, color=AppColors.OUTLINE)
    TEXT_FIELD_HEIGHT = max(
        AppDimensions.CONTROL_HEIGHT,
        math.ceil((INPUT_FONT_SIZE * INPUT_FONT_LINE_HEIGHT) + (2 * AppDimensions.PADDING_INPUT_VERTICAL) + 2),
    )
    VALIDATION_ERROR_EXTRA_HEIGHT = math.ceil((INPUT_FONT_SIZE * INPUT_FONT_LINE_HEIGHT) + AppDimensions.SPACE_2XS)
    FIELD_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )
    DISABLED_CONTENT_OPACITY = 0.5


class DialogStyles:
    MODAL = False
    ELEVATION = 24
    ALIGNMENT = AlignmentStyles.CENTER
    CONTENT_ALIGNMENT = AlignmentStyles.AXIS_START
    CONTENT_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    ACTIONS_ALIGNMENT = AlignmentStyles.AXIS_END
    CONTENT_SPACING = 14
    SCROLLABLE = False

    INSET_HORIZONTAL = 56
    INSET_VERTICAL = 32
    INSET_PADDING = ft.Padding.symmetric(horizontal=INSET_HORIZONTAL, vertical=INSET_VERTICAL)

    TITLE_HORIZONTAL = 32
    TITLE_TOP = 30
    TITLE_PADDING = ft.Padding.only(
        left=TITLE_HORIZONTAL,
        top=TITLE_TOP,
        right=TITLE_HORIZONTAL,
        bottom=0,
    )

    CONTENT_HORIZONTAL = 32
    CONTENT_TOP = 24
    CONTENT_BOTTOM = 28
    CONTENT_PADDING = ft.Padding.only(
        left=CONTENT_HORIZONTAL,
        top=CONTENT_TOP,
        right=CONTENT_HORIZONTAL,
        bottom=CONTENT_BOTTOM,
    )

    ACTIONS_HORIZONTAL = 32
    ACTIONS_TOP = 12
    ACTIONS_BOTTOM = 20
    ACTIONS_PADDING = ft.Padding.only(
        left=ACTIONS_HORIZONTAL,
        top=ACTIONS_TOP,
        right=ACTIONS_HORIZONTAL,
        bottom=ACTIONS_BOTTOM,
    )
    ACTION_BUTTON_PADDING = ft.Padding.symmetric(horizontal=8, vertical=8)
    ACTIONS_OVERFLOW_BUTTON_SPACING = 12

    LOADING_ACTIONS_PADDING = ft.Padding.all(0)
    LOADING_ACTION_BUTTON_PADDING = ft.Padding.all(0)
    LOADING_ACTIONS_OVERFLOW_BUTTON_SPACING = 0
    LOADING_SCROLLABLE = False


class MenuStyles:
    flat = ft.MenuStyle(
        shape=ft.RoundedRectangleBorder(radius=0),
        elevation=0,
        shadow_color=ft.Colors.TRANSPARENT,
        padding=ft.Padding.all(0),
        bgcolor=AppColors.SURFACE,
        alignment=AlignmentStyles.TOP_LEFT,
    )
