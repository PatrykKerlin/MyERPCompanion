import math
from typing import cast

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
    top_bar_info = ft.ButtonStyle(
        padding=ft.Padding.only(
            left=AppDimensions.SPACE_SM,
            top=0,
            right=AppDimensions.SPACE_MD,
            bottom=0,
        ),
        color=AppColors.ON_MATERIAL_BLUE,
        bgcolor=ft.Colors.TRANSPARENT,
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
    add_to_cart = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL,
        ),
        bgcolor={
            ft.ControlState.DEFAULT: AppColors.MATERIAL_BLUE,
            ft.ControlState.DISABLED: AppColors.SURFACE_CONTAINER_HIGH,
        },
        color={
            ft.ControlState.DEFAULT: AppColors.ON_MATERIAL_BLUE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
            ft.ControlState.DISABLED: ft.BorderSide(1, AppColors.OUTLINE),
        },
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )


class AlignmentStyles:
    CENTER = ft.Alignment.CENTER
    CENTER_LEFT = ft.Alignment.CENTER_LEFT
    CENTER_RIGHT = ft.Alignment.CENTER_RIGHT
    TOP_LEFT = ft.Alignment.TOP_LEFT
    TOP_RIGHT = ft.Alignment.TOP_RIGHT
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
    INPUT_FONT_SIZE = 14
    INPUT_FONT_LINE_HEIGHT = 1.2
    INPUT_TEXT_STYLE = ft.TextStyle(size=INPUT_FONT_SIZE, height=INPUT_FONT_LINE_HEIGHT)
    FIELD_BORDER_RADIUS = AppDimensions.RADIUS_MD
    FIELD_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    FIELD_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY
    FIELD_BORDER_SIDE = ft.BorderSide(width=1.25, color=AppColors.OUTLINE)
    TEXT_FIELD_HEIGHT = max(
        AppDimensions.CONTROL_HEIGHT,
        math.ceil((INPUT_FONT_SIZE * INPUT_FONT_LINE_HEIGHT) + (2 * AppDimensions.PADDING_INPUT_VERTICAL) + 2),
    )
    FIELD_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_INPUT_HORIZONTAL,
        vertical=AppDimensions.PADDING_INPUT_VERTICAL,
    )


class TypographyStyles:
    APP_HEADER = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
    PAGE_TITLE = ft.TextStyle(size=26, weight=ft.FontWeight.BOLD)
    AUTH_TITLE = ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
    SECTION_TITLE = ft.TextStyle(weight=ft.FontWeight.BOLD)
    SECTION_TITLE_SEMIBOLD = ft.TextStyle(weight=ft.FontWeight.W_600)
    LEGEND_TITLE = ft.TextStyle(size=11, weight=ft.FontWeight.W_600)
    LEGEND_TEXT = ft.TextStyle(size=11)
    FOOTER_TITLE = ft.TextStyle(size=12, weight=ft.FontWeight.W_600)
    FOOTER_TEXT = ft.TextStyle(size=11)


class DialogStyles:
    MODAL = True
    ELEVATION = 24
    ALIGNMENT = AlignmentStyles.CENTER
    CONTENT_ALIGNMENT = AlignmentStyles.AXIS_START
    CONTENT_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    ACTIONS_ALIGNMENT = AlignmentStyles.AXIS_END
    CONTENT_SPACING = AppDimensions.SPACE_XL
    SCROLLABLE = True

    INSET_PADDING = ft.Padding.symmetric(horizontal=60, vertical=42)
    TITLE_PADDING = ft.Padding.only(left=38, top=28, right=38, bottom=6)
    CONTENT_PADDING = ft.Padding.only(left=38, top=26, right=38, bottom=24)
    CONTENT_INNER_PADDING = ft.Padding.symmetric(horizontal=14, vertical=10)
    ACTIONS_PADDING = ft.Padding.only(left=38, top=16, right=38, bottom=24)
    ACTION_BUTTON_PADDING = ft.Padding.symmetric(horizontal=12, vertical=10)
    ACTIONS_OVERFLOW_BUTTON_SPACING = 16


class AppViewStyles:
    AUTH_OVERLAY_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.AUTH_OVERLAY_PADDING_HORIZONTAL,
        vertical=AppDimensions.AUTH_OVERLAY_PADDING_VERTICAL,
    )
    TOP_BAR_ICON_SIZE = AppDimensions.CART_BUTTON_ICON_SIZE
    TOP_BAR_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_FORM_HORIZONTAL,
        vertical=AppDimensions.PADDING_FORM_VERTICAL,
    )
    TOP_BAR_BORDER = ft.Border(bottom=ft.BorderSide(1, AppColors.OUTLINE_VARIANT))
    FOOTER_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.PADDING_FORM_HORIZONTAL,
        vertical=AppDimensions.PADDING_BUTTON_VERTICAL,
    )
    FOOTER_BORDER = ft.Border(top=ft.BorderSide(1, AppColors.OUTLINE_VARIANT))
    CLICKABLE_TEXT_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_2XS)
    FOOTER_MUTED_TEXT_COLOR: ft.ColorValue = AppColors.ON_SURFACE_VARIANT
    TOP_BAR_ACTION_COLOR: ft.ColorValue = AppColors.ON_MATERIAL_BLUE


class AuthViewStyles:
    HERO_BODY_PADDING = ft.Padding.symmetric(
        horizontal=AppDimensions.AUTH_CARD_PADDING_HORIZONTAL,
        vertical=AppDimensions.AUTH_CARD_PADDING_VERTICAL,
    )
    HERO_CARD_MARGIN = ft.Margin.symmetric(horizontal=AppDimensions.SPACE_XL, vertical=AppDimensions.SPACE_LG)
    HERO_CARD_BGCOLOR: ft.ColorValue = AppColors.CARD


class OrdersViewStyles:
    STATUS_LOADING_PADDING = ft.Padding.only(bottom=AppDimensions.SPACE_SM)
    PAYMENT_LEGEND_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_SM, vertical=AppDimensions.SPACE_XS)
    PAYMENT_LEGEND_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    PAYMENT_LEGEND_RADIUS = AppDimensions.RADIUS_MD
    PANEL_PADDING = ft.Padding.all(AppDimensions.SPACE_LG)
    PANEL_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    PANEL_RADIUS = AppDimensions.RADIUS_MD
    STATUS_COLUMN_BORDER = ft.Border(left=ft.BorderSide(1, AppColors.OUTLINE_VARIANT))
    STATUS_COLUMN_PADDING = ft.Padding.only(left=AppDimensions.SPACE_LG)
    CARD_ELEVATION = 2
    CARD_BGCOLOR: ft.ColorValue = AppColors.CARD
    CARD_PADDING = ft.Padding.all(AppDimensions.PADDING_FORM_VERTICAL)
    ORDER_TILE_PADDING = ft.Padding.all(AppDimensions.SPACE_MD)
    ORDER_TILE_RADIUS = AppDimensions.RADIUS_MD
    ORDER_META_HEADER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_SM)
    ORDER_ITEMS_ROW_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_XS, horizontal=AppDimensions.SPACE_SM)
    ORDER_ITEMS_ROW_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    ORDER_ITEMS_ROW_RADIUS = AppDimensions.RADIUS_SM
    STATUS_ROW_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)
    STATUS_ROW_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    STATUS_ROW_RADIUS = AppDimensions.RADIUS_SM
    ITEM_DIALOG_FALLBACK_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)
    OVERDUE_COLOR: ft.ColorValue = AppColors.ERROR
    ORDER_SELECTED_BGCOLOR: ft.ColorValue = AppColors.PRIMARY_CONTAINER
    UNPAID_ICON: ft.IconData = ft.Icons.REQUEST_QUOTE
    UNPAID_LEGEND_ICON_SIZE = 16
    UNPAID_LIST_ICON_SIZE = 22
    OVERDUE_LEGEND_ICON_SIZE = 16
    OVERDUE_LIST_ICON_SIZE = 22

    @staticmethod
    def order_tile_border(selected: bool) -> ft.Border:
        color = AppColors.PRIMARY if selected else AppColors.OUTLINE_VARIANT
        return ft.Border.all(1, color)

    @staticmethod
    def order_tile_bgcolor(selected: bool) -> ft.ColorValue | None:
        if selected:
            return OrdersViewStyles.ORDER_SELECTED_BGCOLOR
        return None


class CreateOrderViewStyles:
    CARD_ELEVATION = 2
    CARD_BGCOLOR: ft.ColorValue = AppColors.CARD
    CARD_PADDING = ft.Padding.all(AppDimensions.PADDING_FORM_VERTICAL)
    ROOT_ALIGNMENT = AlignmentStyles.CENTER
    LEFT_ALIGNMENT = AlignmentStyles.CENTER_LEFT
    CENTER_ALIGNMENT = AlignmentStyles.CENTER
    RIGHT_ALIGNMENT = AlignmentStyles.CENTER_RIGHT
    CONTENT_SPACING = AppDimensions.SPACE_SM

    RESPONSIVE_COLUMNS = 12
    RESPONSIVE_ALIGNMENT = AlignmentStyles.AXIS_START
    RESPONSIVE_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    RESPONSIVE_SPACING = AppDimensions.SPACE_2XS
    RESPONSIVE_RUN_SPACING = AppDimensions.SPACE_2XS

    HEADER_BACK_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 12, "md": 2})
    HEADER_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 12, "md": 10})

    CART_ITEM_NAME_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 12, "md": 3})
    CART_ITEM_QUANTITY_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 6, "md": 3})
    CART_ITEM_DISCOUNTS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 12, "md": 5})
    CART_ITEM_REMOVE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 6, "md": 1})

    CHECKOUT_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 12, "md": 4})
    CHECKOUT_TOTAL_LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 6, "md": 4})
    CHECKOUT_TOTAL_VALUE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": 6, "md": 8})
    CHECKOUT_TOTAL_ROW_SPACING = 0
    CHECKOUT_TOTAL_ROW_RUN_SPACING = 0

    DETAILS_COLUMN_SPACING = AppDimensions.SPACE_2XS
    CART_HEADER_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_2XS, horizontal=AppDimensions.SPACE_XS)
    CART_ITEM_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_XS, horizontal=AppDimensions.SPACE_XS)
    CART_ITEM_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)

    CART_DIALOG_WIDTH_RATIO = 0.95
    CART_DIALOG_BREAKPOINT_DESKTOP = 900
    CART_DIALOG_MAX_WIDTH = 960
    CART_DIALOG_MIN_VIEWPORT_WIDTH = 320
    CART_DIALOG_CONTENT_WIDTH_RATIO = 0.72
    CART_DIALOG_CONTENT_MIN_WIDTH = 380
    CART_DIALOG_DEFAULT_WIDTH = 460
    CART_DIALOG_HEIGHT_RATIO = 0.5

    CHECKOUT_DIALOG_MIN_WIDTH = 360
    CHECKOUT_DIALOG_WIDTH_RATIO = 0.9
    CHECKOUT_DIALOG_MAX_WIDTH = 720
    CHECKOUT_DIALOG_DEFAULT_WIDTH = 600

    CHECKOUT_ERROR_COLOR: ft.ColorValue = AppColors.ERROR
    CHECKOUT_MISSING_RATE_PADDING = ft.Padding.only(top=AppDimensions.SPACE_2XS)
    ITEM_IMAGE_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    ITEM_ROW_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)


class FeedbackStyles:
    ERROR_ICON_COLOR: ft.ColorValue = AppColors.ERROR
