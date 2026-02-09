from collections.abc import Callable

import flet as ft

from utils.enums import View
from utils.translation import Translation


class AppView:
    __MOBILE_WIDTH = 360
    __MOBILE_HEIGHT = 800
    __MENU_ITEMS: list[tuple[View, str]] = [
        (View.BINS, "bins"),
        (View.ITEMS, "items"),
        (View.BIN_TRANSFER, "bin_transfer"),
        (View.ORDER_PICKING, "order_picking"),
        (View.STOCK_RECEIVING, "stock_receiving"),
    ]

    def __init__(self, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__on_view_selected: Callable[[View], None] | None = None
        self.__drawer_views: list[View] = []

        self.__title_text = ft.Text(
            self.__translation.get("my_erp_companion"),
            size=18,
            weight=ft.FontWeight.W_600,
        )
        self.__menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            on_click=self.__open_navigation_drawer,
        )
        self.__drawer = ft.NavigationDrawer(controls=[], on_change=self.__on_drawer_change)
        self.__top_bar = ft.Container(
            visible=False,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
            content=ft.Row(
                controls=[self.__menu_button, self.__title_text],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
        )

        self.__body_container = ft.Container(expand=True, alignment=ft.Alignment.TOP_LEFT)
        self.__content = ft.Column(
            controls=[self.__top_bar, self.__body_container],
            expand=True,
            spacing=0,
            visible=False,
        )
        self.__auth_container = ft.Container(visible=False, expand=True, alignment=ft.Alignment.CENTER)
        self.__root = ft.Stack(
            controls=[self.__content, self.__auth_container],
            expand=True,
            fit=ft.StackFit.EXPAND,
        )
        self.__refresh_drawer_controls()

    def build(self) -> ft.Control:
        page = ft.context.page
        self._apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__title_text.value = self.__translation.get("my_erp_companion")
        self.__refresh_drawer_controls()
        content = self.__body_container.content
        target = content
        if isinstance(content, ft.Container):
            target = content.content
        if target is not None and hasattr(target, "update_translation"):
            update_translation = getattr(target, "update_translation")
            if callable(update_translation):
                update_translation(translation)

    def set_navigation_handler(self, on_view_selected: Callable[[View], None]) -> None:
        self.__on_view_selected = on_view_selected
        self.__refresh_drawer_controls()

    def set_navigation_visible(self, visible: bool) -> None:
        self.__top_bar.visible = visible
        self.__safe_update(self.__top_bar)

    def set_auth_view(self, component: ft.Control | None) -> None:
        if component is None:
            self.__auth_container.content = None
        else:
            self.__auth_container.content = ft.Container(
                content=component,
                alignment=ft.Alignment.CENTER,
                expand=False,
            )
        self.__auth_container.visible = component is not None

    def set_content(self, component: ft.Control | None) -> None:
        if component is None:
            self.__body_container.content = None
        else:
            self.__body_container.content = ft.Container(
                content=component,
                expand=True,
                alignment=ft.Alignment.TOP_LEFT,
            )
        self.__safe_update(self.__body_container)

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self._resolve_theme_mode(theme)
        page.update()

    def set_content_visible(self, visible: bool) -> None:
        self.__content.visible = visible
        self.__safe_update(self.__content)

    def _apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self._resolve_theme_mode(self.__theme)
        page.padding = 0
        page.spacing = 0
        page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.bgcolor = ft.Colors.SURFACE
        page.drawer = self.__drawer

        if bool(getattr(page, "web", False)):
            return

        page.window.width = self.__MOBILE_WIDTH
        page.window.height = self.__MOBILE_HEIGHT
        page.window.min_width = self.__MOBILE_WIDTH
        page.window.min_height = self.__MOBILE_HEIGHT
        page.window.resizable = False

    def _resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM

    def __refresh_drawer_controls(self) -> None:
        self.__drawer_views = []
        controls: list[ft.Control] = [
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                content=ft.Text(self.__translation.get("my_erp_companion"), weight=ft.FontWeight.W_600),
            ),
            ft.Divider(height=1),
        ]

        for view_key, label_key in self.__MENU_ITEMS:
            controls.append(
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    selected_icon=ft.Icons.CHEVRON_RIGHT,
                    label=self.__translation.get(label_key),
                )
            )
            self.__drawer_views.append(view_key)

        self.__drawer.controls = controls
        if self.__drawer.selected_index < 0:
            self.__drawer.selected_index = 0
        self.__safe_update(self.__drawer)

    async def __open_navigation_drawer(self, _: ft.ControlEvent) -> None:
        page = self.__root.page
        if not page:
            return
        page.drawer = self.__drawer
        await page.show_drawer()

    async def __on_drawer_change(self, _: ft.ControlEvent) -> None:
        index = self.__drawer.selected_index
        if not isinstance(index, int):
            return
        if index < 0 or index >= len(self.__drawer_views):
            return
        selected_view = self.__drawer_views[index]
        if self.__on_view_selected:
            self.__on_view_selected(selected_view)
        page = self.__root.page
        if page:
            await page.close_drawer()

    @staticmethod
    def __safe_update(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
