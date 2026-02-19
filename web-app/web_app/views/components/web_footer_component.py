from datetime import datetime

import flet as ft
from controllers.base.base_controller import BaseController
from styles.styles import AlignmentStyles, AppViewStyles, TypographyStyles
from utils.translation import Translation
from views.base.base_component import BaseComponent


class WebFooterComponent(BaseComponent[BaseController], ft.Container):
    def __init__(self, controller: BaseController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__footer_app_name = ft.Text(self._translation.get("my_erp_companion"), style=TypographyStyles.FOOTER_TITLE)
        self.__footer_portal = ft.Text(
            self._translation.get("footer_web_portal"),
            style=TypographyStyles.FOOTER_TEXT,
            color=AppViewStyles.FOOTER_MUTED_TEXT_COLOR,
        )
        self.__footer_copy = ft.Text(
            self.__build_footer_copy(),
            style=TypographyStyles.FOOTER_TEXT,
            color=AppViewStyles.FOOTER_MUTED_TEXT_COLOR,
        )
        ft.Container.__init__(
            self,
            padding=AppViewStyles.FOOTER_PADDING,
            border=AppViewStyles.FOOTER_BORDER,
            content=ft.ResponsiveRow(
                columns=12,
                controls=[
                    ft.Container(
                        col={"sm": 12, "md": 7},
                        content=ft.Column(
                            spacing=0,
                            tight=True,
                            controls=[self.__footer_app_name, self.__footer_portal],
                        ),
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        alignment=AlignmentStyles.CENTER_RIGHT,
                        content=self.__footer_copy,
                    ),
                ],
            ),
        )

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__footer_app_name.value = self._translation.get("my_erp_companion")
        self.__footer_portal.value = self._translation.get("footer_web_portal")
        self.__footer_copy.value = self.__build_footer_copy()
        self._safe_update(self)

    def __build_footer_copy(self) -> str:
        year = datetime.now().year
        app_name = self._translation.get("my_erp_companion")
        rights = self._translation.get("all_rights_reserved")
        return f"(c) {year} {app_name}. {rights}"
