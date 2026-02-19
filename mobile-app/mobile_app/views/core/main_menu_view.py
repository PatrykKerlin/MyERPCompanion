import flet as ft
from styles.styles import MainMenuViewStyles, TypographyStyles
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.mixins.input_controls_mixin import InputControlsMixin


class MainMenuView(InputControlsMixin, ft.Container):
    def __init__(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title = self._get_label(
            self.__translation.get("my_erp_companion"),
            style=MainMenuViewStyles.TITLE_STYLE,
            text_align=MainMenuViewStyles.HINT_ALIGN,
        )

        self.__summary_title = self._get_label(
            self.__translation.get("order_picking"),
            style=MainMenuViewStyles.SUMMARY_TITLE_STYLE,
            text_align=ft.TextAlign.LEFT,
        )
        self.__orders_label = self._get_label(self.__translation.get("orders_to_pick"))
        self.__items_label = self._get_label(self.__translation.get("distinct_items_to_pick"))
        self.__pieces_label = self._get_label(self.__translation.get("total_pieces_to_pick"))

        self.__orders_value = self._get_label("0", style=TypographyStyles.VALUE_BOLD)
        self.__items_value = self._get_label("0", style=TypographyStyles.VALUE_BOLD)
        self.__pieces_value = self._get_label("0", style=TypographyStyles.VALUE_BOLD)

        self.__summary_section = ft.Container(
            padding=MainMenuViewStyles.SUMMARY_PADDING,
            border=MainMenuViewStyles.SUMMARY_BORDER,
            border_radius=MainMenuViewStyles.SUMMARY_BORDER_RADIUS,
            content=ft.Column(
                controls=[
                    self.__summary_title,
                    self.__build_summary_row(self.__orders_label, self.__orders_value),
                    self.__build_summary_row(self.__items_label, self.__items_value),
                    self.__build_summary_row(self.__pieces_label, self.__pieces_value),
                ],
                tight=True,
                spacing=MainMenuViewStyles.SUMMARY_SPACING,
            ),
        )
        self.__summary_row = ft.ResponsiveRow(
            controls=[ft.Container(content=self.__summary_section, col=MainMenuViewStyles.SUMMARY_COL)],
            columns=MainMenuViewStyles.SUMMARY_ROW_COLUMNS,
            alignment=MainMenuViewStyles.SUMMARY_CONTAINER_ROW_ALIGNMENT,
            vertical_alignment=MainMenuViewStyles.SUMMARY_CONTAINER_ROW_VERTICAL_ALIGNMENT,
        )

        ft.Container.__init__(
            self,
            expand=True,
            alignment=MainMenuViewStyles.ROOT_ALIGNMENT,
            padding=MainMenuViewStyles.ROOT_PADDING,
            content=ft.Column(
                controls=[self.__title, self.__summary_row],
                tight=True,
                spacing=MainMenuViewStyles.ROOT_SPACING,
                horizontal_alignment=MainMenuViewStyles.ROOT_HORIZONTAL_ALIGNMENT,
            ),
        )

    def set_summary(self, orders_count: int, items_count: int, pieces_count: int) -> None:
        self.__orders_value.value = str(max(0, orders_count))
        self.__items_value.value = str(max(0, items_count))
        self.__pieces_value.value = str(max(0, pieces_count))
        BaseComponent.safe_update(self)

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title.value = self.__translation.get("my_erp_companion")
        self.__summary_title.value = self.__translation.get("order_picking")
        self.__orders_label.value = self.__translation.get("orders_to_pick")
        self.__items_label.value = self.__translation.get("distinct_items_to_pick")
        self.__pieces_label.value = self.__translation.get("total_pieces_to_pick")
        BaseComponent.safe_update(self)

    @staticmethod
    def __build_summary_row(label: ft.Text, value: ft.Text) -> ft.Control:
        return ft.Row(
            controls=[label, value],
            alignment=MainMenuViewStyles.SUMMARY_ROW_ALIGNMENT,
            vertical_alignment=MainMenuViewStyles.SUMMARY_ROW_VERTICAL_ALIGNMENT,
        )
