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
        bgcolor={
            ft.ControlState.DEFAULT: AppColors.SURFACE_CONTAINER_HIGH,
            ft.ControlState.DISABLED: AppColors.SURFACE,
        },
        color={
            ft.ControlState.DEFAULT: AppColors.ON_SURFACE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(width=1, color=AppColors.OUTLINE),
            ft.ControlState.DISABLED: ft.BorderSide(width=1, color=AppColors.OUTLINE_VARIANT),
        },
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    compact = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL_COMPACT,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL_COMPACT,
        ),
        bgcolor={
            ft.ControlState.DEFAULT: AppColors.SURFACE_CONTAINER_HIGH,
            ft.ControlState.DISABLED: AppColors.SURFACE,
        },
        color={
            ft.ControlState.DEFAULT: AppColors.ON_SURFACE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(width=1, color=AppColors.OUTLINE),
            ft.ControlState.DISABLED: ft.BorderSide(width=1, color=AppColors.OUTLINE_VARIANT),
        },
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
        color={
            ft.ControlState.DEFAULT: AppColors.ON_SURFACE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        bgcolor=ft.Colors.TRANSPARENT,
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    primary_regular = ft.ButtonStyle(
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
            ft.ControlState.DISABLED: ft.BorderSide(1, AppColors.OUTLINE_VARIANT),
        },
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    primary_compact = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL_COMPACT,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL_COMPACT,
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
            ft.ControlState.DISABLED: ft.BorderSide(1, AppColors.OUTLINE_VARIANT),
        },
        shape=ft.RoundedRectangleBorder(radius=AppDimensions.RADIUS_MD),
    )
    add_to_cart = ft.ButtonStyle(
        padding=ft.Padding.symmetric(
            horizontal=AppDimensions.PADDING_BUTTON_HORIZONTAL,
            vertical=AppDimensions.PADDING_BUTTON_VERTICAL,
        ),
        bgcolor={
            ft.ControlState.DEFAULT: AppColors.MATERIAL_BLUE,
            ft.ControlState.DISABLED: AppColors.SURFACE,
        },
        color={
            ft.ControlState.DEFAULT: AppColors.ON_MATERIAL_BLUE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
            ft.ControlState.DISABLED: ft.BorderSide(1, AppColors.OUTLINE_VARIANT),
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
    LOADING_ACTIONS_PADDING = ft.Padding.all(0)
    LOADING_ACTION_BUTTON_PADDING = ft.Padding.all(0)
    LOADING_ACTIONS_OVERFLOW_BUTTON_SPACING = 0
    LOADING_SCROLLABLE = False
    CURRENT_USER_SETTINGS_CONTENT_WIDTH = 540
    ITEM_DETAILS_CONTENT_WIDTH = 380
    ITEM_DETAILS_LABEL_WIDTH = 150
    ITEM_DETAILS_VALUE_WIDTH = ITEM_DETAILS_CONTENT_WIDTH - ITEM_DETAILS_LABEL_WIDTH - AppDimensions.SPACE_MD
    ITEM_DETAILS_SCROLL_HEIGHT = 360
    ITEM_DETAILS_GALLERY_VISIBLE_COUNT = 3


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
    FOOTER_ROW_COLUMNS = 12
    FOOTER_LEFT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 7, "lg": 7, "xl": 7})
    FOOTER_RIGHT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 5, "lg": 5, "xl": 5})
    FOOTER_LEFT_COLUMN_SPACING = 0
    CLICKABLE_TEXT_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_2XS)
    FOOTER_MUTED_TEXT_COLOR: ft.ColorValue = AppColors.ON_SURFACE_VARIANT


class AuthViewStyles:
    HERO_CARD_WIDTH = int(AppDimensions.AUTH_CARD_WIDTH * 0.825)
    ROOT_ROW_COLUMNS = 12
    HERO_CARD_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 6, "lg": 4, "xl": 3})
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
    CARD_OUTER_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_SM)
    CARD_CONTENT_SPACING = AppDimensions.SPACE_LG
    DETAILS_ROW_COLUMNS = 12
    DETAILS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    PANELS_ROW_COLUMNS = 12
    PANELS_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    PANELS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    ROOT_ROW_COLUMNS = 12
    ROOT_ROW_ALIGNMENT = AlignmentStyles.AXIS_CENTER
    ORDER_TILE_PADDING = ft.Padding.all(AppDimensions.SPACE_MD)
    ORDER_TILE_RADIUS = AppDimensions.RADIUS_MD
    ORDER_TILE_ROW_COLUMNS = 12
    ORDER_TILE_ROW_SPACING = AppDimensions.SPACE_SM
    ORDER_TILE_TEXT_SPACING = AppDimensions.SPACE_2XS
    ORDER_META_HEADER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_SM)
    ITEMS_HEADER_ROW_COLUMNS = 12
    ITEMS_HEADER_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    ITEMS_HEADER_ROW_SPACING = AppDimensions.SPACE_LG
    ORDER_ITEMS_ROW_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_XS, horizontal=AppDimensions.SPACE_SM)
    ORDER_ITEMS_ROW_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    ORDER_ITEMS_ROW_RADIUS = AppDimensions.RADIUS_SM
    ITEMS_ROW_COLUMNS = 12
    ITEMS_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    ITEMS_ROW_SPACING = AppDimensions.SPACE_LG
    STATUS_ROW_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)
    STATUS_ROW_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    STATUS_ROW_RADIUS = AppDimensions.RADIUS_SM
    META_AND_NOTES_SECTION_EXPAND = 11
    META_AND_NOTES_ROW_COLUMNS = 12
    META_AND_NOTES_ROW_SPACING = AppDimensions.SPACE_LG
    META_AND_NOTES_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    DETAILS_SECTION_EXPAND = 9
    META_CONTAINER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 8, "lg": 8, "xl": 8})
    NOTES_CONTAINER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    NOTES_CONTAINER_PADDING = ft.Padding.only(left=AppDimensions.SPACE_LG)
    META_ROW_COLUMNS = 12
    META_ROW_SPACING = AppDimensions.SPACE_LG
    META_TRAILING_SPACING = AppDimensions.SPACE_SM
    ITEM_DIALOG_FALLBACK_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)
    OVERDUE_COLOR: ft.ColorValue = AppColors.ERROR
    ORDER_SELECTED_BGCOLOR: ft.ColorValue = AppColors.PRIMARY_CONTAINER
    UNPAID_ICON: ft.IconData = ft.Icons.REQUEST_QUOTE
    UNPAID_LEGEND_ICON_SIZE = 16
    UNPAID_LIST_ICON_SIZE = 22
    OVERDUE_LEGEND_ICON_SIZE = 16
    OVERDUE_LIST_ICON_SIZE = 22
    ORDER_TILE_TEXT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 11, "lg": 11, "xl": 11})
    ORDER_TILE_ICON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 1, "lg": 1, "xl": 1})
    ORDER_META_LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    ORDER_META_VALUE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 8, "lg": 8, "xl": 8})
    ORDER_ITEM_INDEX_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ORDER_ITEM_NAME_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ORDER_ITEM_EAN_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ORDER_ITEM_QUANTITY_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ORDER_ITEM_DISCOUNTS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    CARD_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 11, "lg": 10, "xl": 9})
    PANELS_LEFT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 3, "lg": 3, "xl": 3})
    PANELS_RIGHT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 9, "lg": 9, "xl": 9})
    DETAILS_ITEMS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 8, "lg": 8, "xl": 8})
    DETAILS_STATUS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})

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
    ROOT_ROW_COLUMNS = 12
    ROOT_ROW_ALIGNMENT = AlignmentStyles.AXIS_CENTER
    CARD_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 11, "lg": 10, "xl": 9})
    CARD_OUTER_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_SM)

    HEADER_BACK_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    HEADER_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 3, "lg": 3, "xl": 3})
    HEADER_SPACER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 7, "lg": 7, "xl": 7})

    CART_COLUMNS = 9
    CART_ITEM_NAME_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 3, "lg": 3, "xl": 3})
    CART_ITEM_QUANTITY_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    CART_ITEM_DISCOUNTS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 3, "lg": 3, "xl": 3})
    CART_ITEM_REMOVE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 1, "lg": 1, "xl": 1})

    CHECKOUT_FILTER_COLUMNS = 15
    CHECKOUT_CURRENCY_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    CHECKOUT_CUSTOMER_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 5, "lg": 5, "xl": 5})
    CHECKOUT_FILTER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 6, "lg": 6, "xl": 6})
    CHECKOUT_TOTAL_LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    CHECKOUT_TOTAL_VALUE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 8, "lg": 8, "xl": 8})
    CHECKOUT_TOTAL_ROW_SPACING = 0
    CHECKOUT_TOTAL_ROW_RUN_SPACING = 0
    ITEM_ROW_IMAGE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 1, "lg": 1, "xl": 1})
    ITEM_ROW_DETAILS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ITEM_ROW_CATEGORY_DISCOUNT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ITEM_ROW_ITEM_DISCOUNT_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})
    ITEM_ROW_QUANTITY_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 3, "lg": 3, "xl": 3})
    ITEM_ROW_ADD_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 2, "lg": 2, "xl": 2})

    DETAILS_COLUMN_SPACING = AppDimensions.SPACE_2XS
    CART_HEADER_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_2XS, horizontal=AppDimensions.SPACE_XS)
    CART_ITEM_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_XS, horizontal=AppDimensions.SPACE_XS)
    CART_ITEM_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)

    CART_DIALOG_WIDTH_RATIO = 0.66
    CART_DIALOG_BREAKPOINT_DESKTOP = 900
    CART_DIALOG_MAX_WIDTH = 620
    CART_DIALOG_MIN_VIEWPORT_WIDTH = 320
    CART_DIALOG_CONTENT_WIDTH_RATIO = 0.72
    CART_DIALOG_CONTENT_MIN_WIDTH = 300
    CART_DIALOG_DEFAULT_WIDTH = 320
    CART_DIALOG_MIN_HEIGHT = 120
    CART_DIALOG_HEADER_ESTIMATED_HEIGHT = 52
    CART_DIALOG_ROW_ESTIMATED_HEIGHT = 68
    CART_DIALOG_HEIGHT_RATIO = 0.5

    CHECKOUT_DIALOG_MIN_WIDTH = 360
    CHECKOUT_DIALOG_WIDTH_RATIO = 0.9
    CHECKOUT_DIALOG_MAX_WIDTH = 720
    CHECKOUT_DIALOG_DEFAULT_WIDTH = 600
    CHECKOUT_DIALOG_WIDTH_MULTIPLIER = 1.1

    CHECKOUT_ERROR_COLOR: ft.ColorValue = AppColors.ERROR
    CHECKOUT_MISSING_RATE_PADDING = ft.Padding.only(top=AppDimensions.SPACE_2XS)
    ITEM_IMAGE_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    ITEM_ROW_ELEMENT_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XS)
    ITEM_ROW_DETAILS_PADDING = ft.Padding.only(left=AppDimensions.SPACE_SM, right=AppDimensions.SPACE_XS)
    ITEM_ROW_PADDING = ft.Padding.all(AppDimensions.SPACE_SM)


class FeedbackStyles:
    ERROR_ICON_COLOR: ft.ColorValue = AppColors.ERROR


class CurrentUserSettingsDialogStyles:
    FIELD_BOTTOM_PADDING = ft.Padding.only(bottom=AppDimensions.SPACE_SM)
    ROW_COLUMNS = 12
    ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    ROW_SPACING = AppDimensions.SPACE_LG
    LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 4, "lg": 4, "xl": 4})
    CONTROL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"md": 8, "lg": 8, "xl": 8})
