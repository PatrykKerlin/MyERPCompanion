from __future__ import annotations

from typing import cast

import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions


class AlignmentStyles:
    CENTER = ft.Alignment.CENTER
    TOP_LEFT = ft.Alignment.TOP_LEFT
    TOP_CENTER = ft.Alignment.TOP_CENTER
    CENTER_LEFT = ft.Alignment.CENTER_LEFT
    CENTER_RIGHT = ft.Alignment.CENTER_RIGHT

    AXIS_START = ft.MainAxisAlignment.START
    AXIS_END = ft.MainAxisAlignment.END
    AXIS_CENTER = ft.MainAxisAlignment.CENTER
    AXIS_SPACE_BETWEEN = ft.MainAxisAlignment.SPACE_BETWEEN

    CROSS_START = ft.CrossAxisAlignment.START
    CROSS_CENTER = ft.CrossAxisAlignment.CENTER
    CROSS_STRETCH = ft.CrossAxisAlignment.STRETCH


class TypographyStyles:
    HEADER_TITLE = ft.TextStyle(size=AppDimensions.HEADER_TITLE_SIZE, weight=ft.FontWeight.BOLD)
    HEADER_SUBTITLE = ft.TextStyle(size=AppDimensions.HEADER_SUBTITLE_SIZE)
    APP_TITLE = ft.TextStyle(size=AppDimensions.HEADER_TOP_BAR_TITLE_SIZE, weight=ft.FontWeight.W_600)
    SUMMARY_TITLE = ft.TextStyle(size=AppDimensions.SUMMARY_TITLE_SIZE, weight=ft.FontWeight.W_600)
    PENDING_TITLE = ft.TextStyle(size=AppDimensions.PENDING_TITLE_SIZE, weight=ft.FontWeight.W_600)
    SECTION_TITLE = ft.TextStyle(weight=ft.FontWeight.W_600)
    DETAIL_LABEL = ft.TextStyle(weight=ft.FontWeight.W_600)
    VALUE_BOLD = ft.TextStyle(weight=ft.FontWeight.BOLD)


class ControlStyles:
    FIELD_BORDER_COLOR: ft.ColorValue = AppColors.OUTLINE
    FIELD_FOCUSED_BORDER_COLOR: ft.ColorValue = AppColors.PRIMARY


class ButtonStyles:
    regular = ft.ButtonStyle(
        padding=ft.Padding.symmetric(horizontal=AppDimensions.SPACE_4XL, vertical=AppDimensions.SPACE_MD),
        bgcolor={
            ft.ControlState.DEFAULT: AppColors.CARD,
            ft.ControlState.DISABLED: AppColors.SURFACE,
        },
        color={
            ft.ControlState.DEFAULT: AppColors.ON_SURFACE,
            ft.ControlState.DISABLED: AppColors.ON_SURFACE_VARIANT,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(1, AppColors.OUTLINE),
            ft.ControlState.DISABLED: ft.BorderSide(1, AppColors.OUTLINE_VARIANT),
        },
    )
    primary_regular = ft.ButtonStyle(
        padding=ft.Padding.symmetric(horizontal=AppDimensions.SPACE_4XL, vertical=AppDimensions.SPACE_MD),
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
    )


class BaseDialogStyles:
    MODAL = True
    ALIGNMENT = AlignmentStyles.CENTER
    SCROLLABLE = True

    CONTENT_TIGHT = True
    CONTENT_ALIGNMENT = AlignmentStyles.AXIS_CENTER
    CONTENT_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER


class BaseViewStyles:
    RESPONSIVE_BREAKPOINT = "sm"

    EMPTY_LABEL_SIZE = 0
    EMPTY_INPUT_SIZE = 0

    INPUT_ALIGNMENT = AlignmentStyles.CENTER_LEFT
    SPACING_RESPONSIVE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"sm": AppDimensions.BASE_HIDDEN_FIELD_COL})

    COLUMNS_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    COLUMNS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    GRID_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    GRID_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    MARKER_ANIMATE_SIZE = 300
    MARKER_TOOLTIP_KEY = "check_to_search"

    DROPDOWN_DEFAULT_KEY = "0"
    DROPDOWN_EDITABLE = True
    DROPDOWN_ENABLE_SEARCH = True
    DROPDOWN_ENABLE_FILTER = True

    RADIO_ROW_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    RADIO_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    RADIO_ROW_SPACING = AppDimensions.INPUT_DENSE_SPACING

    CHECKBOX_SHAPE = ft.CircleBorder()


class NumericFieldStyles:
    ALIGNMENT = AlignmentStyles.AXIS_START
    VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START
    SPACING = AppDimensions.SPACE_XS
    ICON_BUTTON_WIDTH = AppDimensions.ICON_BUTTON_WIDTH
    TEXT_ALIGN = ft.TextAlign.CENTER
    BUTTON_ALIGNMENT = AlignmentStyles.TOP_CENTER


class DateFieldStyles:
    ALIGNMENT = AlignmentStyles.AXIS_START
    VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START
    SPACING = AppDimensions.SPACE_SM
    ICON_BUTTON_WIDTH = AppDimensions.ICON_BUTTON_WIDTH
    TEXT_ALIGN = ft.TextAlign.CENTER
    BUTTON_ALIGNMENT = AlignmentStyles.TOP_CENTER


class MobileCommonViewStyles:
    HEADER_TEXTS_SPACING = AppDimensions.SPACE_2XS
    HEADER_ROW_COLUMNS = 12
    HEADER_TEXTS_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 8.0, "sm": 9.0})
    HEADER_ACTION_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 4.0, "sm": 3.0})
    HEADER_ROW_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    HEADER_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START
    HEADER_BACK_ALIGNMENT = AlignmentStyles.CENTER_RIGHT

    LIST_SPACING = AppDimensions.SPACE_MD
    LIST_ITEM_BGCOLOR: ft.ColorValue = AppColors.CARD
    SECTION_SPACING = AppDimensions.SPACE_MD
    DIVIDER_HEIGHT = AppDimensions.DIVIDER_HEIGHT
    DETAILS_VALUE_TEXT_SELECTABLE = True


class AppViewStyles:
    MENU_TITLE_STYLE = TypographyStyles.APP_TITLE
    USERNAME_STYLE = TypographyStyles.HEADER_SUBTITLE
    USER_MENU_USERNAME_STYLE = ft.TextStyle(color=AppColors.ON_SURFACE, weight=ft.FontWeight.W_600)
    USER_MENU_USERNAME_ICON = ft.Icons.PERSON_OUTLINE
    USER_MENU_USERNAME_ICON_COLOR: ft.ColorValue = AppColors.ON_SURFACE
    USER_MENU_DIVIDER_COLOR: ft.ColorValue = AppColors.OUTLINE_VARIANT
    USER_MENU_DIVIDER_HEIGHT = AppDimensions.DIVIDER_HEIGHT
    USER_MENU_DIVIDER_ITEM_HEIGHT = AppDimensions.SPACE_MD
    USER_MENU_DIVIDER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_SM)

    TOP_BAR_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XL, vertical=AppDimensions.SPACE_MD)
    TOP_BAR_BORDER = ft.Border(bottom=ft.BorderSide(1, AppColors.OUTLINE_VARIANT))

    TOP_BAR_LEFT_SPACING = AppDimensions.SPACE_MD
    TOP_BAR_RIGHT_SPACING = AppDimensions.SPACE_XS
    TOP_BAR_ROW_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    TOP_BAR_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER

    BODY_ALIGNMENT = AlignmentStyles.TOP_LEFT
    BODY_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XL, vertical=AppDimensions.SPACE_MD)
    CONTENT_SPACING = 0
    AUTH_ALIGNMENT = AlignmentStyles.CENTER

    PAGE_PADDING = 0
    PAGE_SPACING = 0
    PAGE_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_STRETCH
    PAGE_VERTICAL_ALIGNMENT = AlignmentStyles.AXIS_START
    PAGE_BGCOLOR: ft.ColorValue = AppColors.SURFACE

    MOBILE_WINDOW_WIDTH = AppDimensions.MOBILE_WIDTH
    MOBILE_WINDOW_HEIGHT = AppDimensions.MOBILE_HEIGHT

    DRAWER_SUBTITLE_SIZE = 13
    DRAWER_SUBTITLE_COLOR: ft.ColorValue = AppColors.ON_SURFACE_VARIANT
    DRAWER_HEADER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_3XL, vertical=AppDimensions.SPACE_XL)
    DRAWER_HEADER_SPACING = AppDimensions.SPACE_2XS
    DRAWER_DIVIDER_HEIGHT = AppDimensions.DIVIDER_HEIGHT


class AuthViewStyles:
    FORM_ROW_COLUMNS = 12
    FORM_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 12.0})

    HERO_ROW_COLUMNS = 12
    HERO_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 10.0})
    HERO_CARD_BGCOLOR: ft.ColorValue = AppColors.CARD

    TITLE_STYLE = ft.TextStyle(size=18, weight=ft.FontWeight.BOLD)
    TITLE_ALIGN = ft.TextAlign.CENTER
    SUBTITLE_ALIGN = ft.TextAlign.CENTER

    FORM_STRETCH = AlignmentStyles.CROSS_STRETCH
    HERO_ALIGNMENT = AlignmentStyles.CENTER
    HERO_PADDING = ft.Padding.all(AppDimensions.SPACE_3XL)
    HERO_FORM_SPACER_HEIGHT = AppDimensions.SPACE_XL
    HERO_COLUMN_TIGHT = True
    HERO_COLUMN_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    HERO_WRAPPER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_4XL, vertical=AppDimensions.SPACE_5XL)
    CENTERED_LAYOUT_SPACING = 0
    CENTERED_LAYOUT_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER


class MainMenuViewStyles:
    SUMMARY_ROW_COLUMNS = 12
    SUMMARY_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 10.0})
    SUMMARY_CONTAINER_ROW_ALIGNMENT = AlignmentStyles.AXIS_CENTER
    SUMMARY_CONTAINER_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START
    SUMMARY_BORDER = ft.Border.all(1, AppColors.OUTLINE_VARIANT)
    SUMMARY_BORDER_RADIUS = AppDimensions.CARD_BORDER_RADIUS
    SUMMARY_PADDING = ft.Padding.all(AppDimensions.SPACE_XL)
    SUMMARY_SPACING = AppDimensions.SPACE_MD

    ROOT_SPACING = AppDimensions.SPACE_2XL
    ROOT_ALIGNMENT = AlignmentStyles.CENTER
    ROOT_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    ROOT_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XS, vertical=AppDimensions.SPACE_SM)

    TITLE_STYLE = TypographyStyles.HEADER_TITLE
    HINT_ALIGN = ft.TextAlign.CENTER
    SUMMARY_TITLE_STYLE = TypographyStyles.SUMMARY_TITLE

    SUMMARY_ROW_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    SUMMARY_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER


class BinsViewStyles:
    FILTER_TEXT_INPUT_SIZE = 8
    FILTER_DIRECTION_INPUT_SIZE = 4

    FILTER_ROW_COLUMNS = 12
    FILTER_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    FILTER_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START


class ItemsViewStyles:
    CATEGORY_FILTER_INPUT_SIZE = 5
    INDEX_FILTER_INPUT_SIZE = 7

    FILTER_ROW_COLUMNS = 12
    FILTER_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    FILTER_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START
    DETAILS_SECTION_SPACING = 0
    GALLERY_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    DETAIL_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER

    DETAILS_DIVIDER_HEIGHT = AppDimensions.DIVIDER_HEIGHT
    DETAILS_LABEL_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XS, vertical=AppDimensions.SPACE_2XS)
    DETAILS_VALUE_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_XS, vertical=AppDimensions.SPACE_2XS)
    DETAILS_WRAPPER_PADDING = ft.Padding.symmetric(horizontal=AppDimensions.SPACE_2XS, vertical=AppDimensions.SPACE_2XS)
    DETAILS_ROW_SPACING = AppDimensions.SPACE_LG
    DETAILS_COL_SPACING = AppDimensions.SPACE_2XS
    DETAILS_PAIR_COLUMNS = 12
    DETAILS_LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 6.0, "sm": 6.0})
    DETAILS_VALUE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 6.0, "sm": 6.0})

    GALLERY_SECTION_SPACING = AppDimensions.SPACE_SM
    GALLERY_CONTROL_SPACING = AppDimensions.SPACE_MD
    GALLERY_THUMB_ROW_SPACING = AppDimensions.SPACE_MD
    GALLERY_THUMB_ROW_RUN_SPACING = AppDimensions.SPACE_MD
    GALLERY_THUMB_ROW_ALIGNMENT = AlignmentStyles.AXIS_CENTER
    GALLERY_THUMB_ASPECT_RATIO = 1.0
    GALLERY_EMPTY_PADDING = ft.Padding.symmetric(vertical=AppDimensions.SPACE_MD)
    GALLERY_THUMB_SIZE = AppDimensions.GALLERY_THUMB_SIZE

    GALLERY_DIALOG_IMAGE_WIDTH = AppDimensions.GALLERY_DIALOG_IMAGE_WIDTH
    GALLERY_DIALOG_IMAGE_HEIGHT = AppDimensions.GALLERY_DIALOG_IMAGE_HEIGHT
    GALLERY_WINDOW_SIZE = AppDimensions.GALLERY_WINDOW_SIZE


class OrderPickingViewStyles:
    ORDER_DATE_INPUT_SIZE = 4
    CUSTOMER_INPUT_SIZE = 4
    ORDER_INPUT_SIZE = 4
    PACKAGE_ITEM_INPUT_SIZE = 8
    PICK_BIN_INPUT_SIZE = 12
    PICK_QUANTITY_INPUT_SIZE = 12

    PACKAGE_ITEM_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 8.0, "sm": 8.0})
    PACKAGE_BUTTON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 4.0, "sm": 4.0})

    ORDERS_ROW_COLUMNS = 12
    ORDERS_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    ORDERS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    PACKAGE_ROW_COLUMNS = 12
    PACKAGE_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    PACKAGE_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER

    PICK_BUTTONS_ROW_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    PICK_BUTTONS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    PICK_BUTTONS_ROW_SPACING = AppDimensions.SPACE_LG
    PICK_BUTTONS_ROW_COLUMNS = 12
    PICK_BACK_BUTTON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 6.0, "sm": 6.0})
    PICK_SAVE_BUTTON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 6.0, "sm": 6.0})

    DETAILS_LABEL_PADDING = ItemsViewStyles.DETAILS_LABEL_PADDING
    DETAILS_VALUE_PADDING = ItemsViewStyles.DETAILS_VALUE_PADDING
    DETAILS_WRAPPER_PADDING = ItemsViewStyles.DETAILS_WRAPPER_PADDING
    DETAILS_ROW_SPACING = ItemsViewStyles.DETAILS_ROW_SPACING
    DETAILS_COL_SPACING = ItemsViewStyles.DETAILS_COL_SPACING
    DETAILS_PAIR_COLUMNS = ItemsViewStyles.DETAILS_PAIR_COLUMNS
    DETAILS_LABEL_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 4.0, "sm": 4.0})
    DETAILS_VALUE_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 8.0, "sm": 8.0})

    GALLERY_SECTION_SPACING = ItemsViewStyles.GALLERY_SECTION_SPACING
    GALLERY_CONTROL_SPACING = ItemsViewStyles.GALLERY_CONTROL_SPACING
    GALLERY_THUMB_ROW_SPACING = ItemsViewStyles.GALLERY_THUMB_ROW_SPACING
    GALLERY_THUMB_ROW_RUN_SPACING = ItemsViewStyles.GALLERY_THUMB_ROW_RUN_SPACING
    GALLERY_THUMB_ROW_ALIGNMENT = ItemsViewStyles.GALLERY_THUMB_ROW_ALIGNMENT
    GALLERY_EMPTY_PADDING = ItemsViewStyles.GALLERY_EMPTY_PADDING
    GALLERY_THUMB_SIZE = ItemsViewStyles.GALLERY_THUMB_SIZE
    GALLERY_DIALOG_IMAGE_WIDTH = ItemsViewStyles.GALLERY_DIALOG_IMAGE_WIDTH
    GALLERY_DIALOG_IMAGE_HEIGHT = ItemsViewStyles.GALLERY_DIALOG_IMAGE_HEIGHT
    GALLERY_WINDOW_SIZE = ItemsViewStyles.GALLERY_WINDOW_SIZE


class BinTransferViewStyles:
    AVAILABLE_TEXT_SIZE = 12
    SOURCE_BIN_INPUT_SIZE = 6
    TARGET_BIN_INPUT_SIZE = 6
    ITEM_INPUT_SIZE = 7
    QUANTITY_INPUT_SIZE = 3

    SOURCE_BIN_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 6.0})
    TARGET_BIN_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 6.0})
    ITEM_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 7.0})
    QUANTITY_INFO_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 8.0, "sm": 3.0})
    ADD_BUTTON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 4.0, "sm": 2.0})

    BINS_ROW_COLUMNS = 12
    BINS_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    BINS_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    FORM_ROW_COLUMNS = 12
    FORM_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    FORM_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    QUANTITY_INFO_ALIGNMENT = AlignmentStyles.TOP_LEFT
    QUANTITY_INFO_COLUMN_SPACING = AppDimensions.SPACE_XS
    QUANTITY_INFO_COLUMN_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    QUANTITY_INFO_TEXT_CONTAINER_ALIGNMENT = AlignmentStyles.CENTER
    QUANTITY_INFO_TEXT_ALIGN = ft.TextAlign.CENTER

    PENDING_HEADER_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    PENDING_HEADER_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    PENDING_ROW_SPACING = AppDimensions.SPACE_MD


class StockReceivingViewStyles:
    AVAILABLE_TEXT_SIZE = 12
    ORDER_INPUT_SIZE = 6
    TARGET_BIN_INPUT_SIZE = 6
    ITEM_INPUT_SIZE = 7
    QUANTITY_INPUT_SIZE = 3

    ORDER_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 6.0})
    TARGET_BIN_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 6.0})
    ITEM_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 12.0, "sm": 7.0})
    QUANTITY_INFO_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 8.0, "sm": 3.0})
    ADD_BUTTON_COL: ft.ResponsiveNumber = cast(ft.ResponsiveNumber, {"xs": 4.0, "sm": 2.0})

    TOP_FORM_ROW_COLUMNS = 12
    TOP_FORM_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    TOP_FORM_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    PICK_FORM_ROW_COLUMNS = 12
    PICK_FORM_ROW_ALIGNMENT = AlignmentStyles.AXIS_START
    PICK_FORM_ROW_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_START

    QUANTITY_INFO_ALIGNMENT = AlignmentStyles.TOP_LEFT
    QUANTITY_INFO_COLUMN_SPACING = AppDimensions.SPACE_XS
    QUANTITY_INFO_COLUMN_HORIZONTAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    QUANTITY_INFO_TEXT_CONTAINER_ALIGNMENT = AlignmentStyles.CENTER
    QUANTITY_INFO_TEXT_ALIGN = ft.TextAlign.CENTER

    PENDING_HEADER_ALIGNMENT = AlignmentStyles.AXIS_SPACE_BETWEEN
    PENDING_HEADER_VERTICAL_ALIGNMENT = AlignmentStyles.CROSS_CENTER
    PENDING_SECTION_SPACING = 0
    PENDING_ROW_SPACING = AppDimensions.SPACE_MD


class UserViewStyles:
    FIELDS_SPACING = AppDimensions.SPACE_LG
    ACTIONS_ALIGNMENT = AlignmentStyles.AXIS_END


class SearchResultsStyles:
    DATA_TABLE_ROW_COLOR: ft.ColorValue = AppColors.CARD
    TABLE_ROW_SCROLL = ft.ScrollMode.AUTO
    TABLE_ROW_EXPAND = True
    ROOT_EXPAND = True
