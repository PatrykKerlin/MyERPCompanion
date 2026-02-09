import flet as ft

from utils.translation import Translation


class MainMenuView(ft.Container):
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
        ft.Container.__init__(
            self,
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                controls=[self.__title, self.__hint],
                tight=True,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title.value = self.__translation.get("my_erp_companion")
        self.__hint.value = self.__translation.get("mobile_main_menu_hint")
        try:
            self.update()
        except RuntimeError:
            return
