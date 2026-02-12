import flet as ft
from utils.translation import Translation


class MainMenuView(ft.Container):
    __SUMMARY_WIDTH = 320

    def __init__(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title = ft.Text(
            self.__translation.get("my_erp_companion"),
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        self.__hint = ft.Text(
            self.__translation.get("mobile_main_menu_hint"),
            text_align=ft.TextAlign.CENTER,
        )

        self.__summary_title = ft.Text(
            self.__translation.get("order_picking"),
            size=16,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.LEFT,
        )
        self.__orders_label = ft.Text(self.__translation.get("orders_to_pick"))
        self.__items_label = ft.Text(self.__translation.get("distinct_items_to_pick"))
        self.__pieces_label = ft.Text(self.__translation.get("total_pieces_to_pick"))

        self.__orders_value = ft.Text("0", weight=ft.FontWeight.BOLD)
        self.__items_value = ft.Text("0", weight=ft.FontWeight.BOLD)
        self.__pieces_value = ft.Text("0", weight=ft.FontWeight.BOLD)

        self.__summary_section = ft.Container(
            width=self.__SUMMARY_WIDTH,
            padding=ft.Padding.all(12),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            content=ft.Column(
                controls=[
                    self.__summary_title,
                    self.__build_summary_row(self.__orders_label, self.__orders_value),
                    self.__build_summary_row(self.__items_label, self.__items_value),
                    self.__build_summary_row(self.__pieces_label, self.__pieces_value),
                ],
                tight=True,
                spacing=8,
            ),
        )

        ft.Container.__init__(
            self,
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[self.__title, self.__hint, self.__summary_section],
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def set_summary(self, orders_count: int, items_count: int, pieces_count: int) -> None:
        self.__orders_value.value = str(max(0, orders_count))
        self.__items_value.value = str(max(0, items_count))
        self.__pieces_value.value = str(max(0, pieces_count))
        self.__safe_update()

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title.value = self.__translation.get("my_erp_companion")
        self.__hint.value = self.__translation.get("mobile_main_menu_hint")
        self.__summary_title.value = self.__translation.get("order_picking")
        self.__orders_label.value = self.__translation.get("orders_to_pick")
        self.__items_label.value = self.__translation.get("distinct_items_to_pick")
        self.__pieces_label.value = self.__translation.get("total_pieces_to_pick")
        self.__safe_update()

    @staticmethod
    def __build_summary_row(label: ft.Text, value: ft.Text) -> ft.Control:
        return ft.Row(
            controls=[label, value],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def __safe_update(self) -> None:
        try:
            _ = self.page
        except RuntimeError:
            return
        try:
            self.update()
        except RuntimeError:
            return
