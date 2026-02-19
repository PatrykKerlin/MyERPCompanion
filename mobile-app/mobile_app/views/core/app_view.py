from collections.abc import Callable

import flet as ft
from styles.styles import AlignmentStyles, AppViewStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.components.navigation_drawer_component import NavigationDrawerComponent
from views.components.top_bar_component import TopBarComponent


class AppView:
    def __init__(self, translation: Translation, theme: str) -> None:
        self.__theme = theme
        self.__translation = translation
        self.__on_refresh: Callable[[], None] | None = None
        self.__on_user_settings: Callable[[], None] | None = None
        self.__on_logout: Callable[[], None] | None = None

        self.__top_bar = TopBarComponent(
            translation=self.__translation,
            on_menu_click=self.__open_navigation_drawer,
            on_refresh_click=self.__handle_refresh,
            on_user_settings_click=self.__handle_user_settings,
            on_logout_click=self.__handle_logout,
        )
        self.__navigation_drawer = NavigationDrawerComponent(translation=self.__translation)

        self.__body_container = ft.Container(
            expand=True,
            alignment=AppViewStyles.BODY_ALIGNMENT,
            padding=AppViewStyles.BODY_PADDING,
        )
        self.__content = ft.Column(
            controls=[self.__top_bar, self.__body_container],
            expand=True,
            spacing=AppViewStyles.CONTENT_SPACING,
            visible=False,
        )
        self.__auth_container = ft.Container(visible=False, expand=True, alignment=AppViewStyles.AUTH_ALIGNMENT)
        self.__root = ft.Stack(
            controls=[self.__content, self.__auth_container],
            expand=True,
            fit=ft.StackFit.EXPAND,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self.__apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__top_bar.update_translation(self.__translation)
        self.__navigation_drawer.update_translation(self.__translation)
        content = self.__body_container.content
        target = content
        if isinstance(content, ft.Container):
            target = content.content
        if target is not None and hasattr(target, "update_translation"):
            update_translation = getattr(target, "update_translation")
            if callable(update_translation):
                update_translation(translation)

    def set_navigation_handler(self, on_view_selected: Callable[[View], None]) -> None:
        self.__navigation_drawer.set_navigation_handler(on_view_selected)

    def set_user_settings_handler(self, on_user_settings: Callable[[], None]) -> None:
        self.__on_user_settings = on_user_settings

    def set_refresh_handler(self, on_refresh: Callable[[], None]) -> None:
        self.__on_refresh = on_refresh

    def set_logout_handler(self, on_logout: Callable[[], None]) -> None:
        self.__on_logout = on_logout

    def set_navigation_visible(self, visible: bool) -> None:
        self.__top_bar.set_navigation_visible(visible)

    def set_username(self, username: str | None) -> None:
        self.__top_bar.set_username(username)

    def set_warehouse_name(self, warehouse_name: str | None) -> None:
        self.__navigation_drawer.set_warehouse_name(warehouse_name)

    def set_auth_view(self, component: ft.Control | None) -> None:
        if component is None:
            self.__auth_container.content = None
        else:
            self.__auth_container.content = ft.Container(
                content=component,
                alignment=AlignmentStyles.CENTER,
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
                alignment=AlignmentStyles.TOP_LEFT,
            )
        BaseComponent.safe_update(self.__body_container)

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self.__resolve_theme_mode(theme)
        page.update()

    def set_content_visible(self, visible: bool) -> None:
        self.__content.visible = visible
        BaseComponent.safe_update(self.__content)

    def __apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self.__resolve_theme_mode(self.__theme)
        page.padding = AppViewStyles.PAGE_PADDING
        page.spacing = AppViewStyles.PAGE_SPACING
        page.horizontal_alignment = AppViewStyles.PAGE_HORIZONTAL_ALIGNMENT
        page.vertical_alignment = AppViewStyles.PAGE_VERTICAL_ALIGNMENT
        page.bgcolor = AppViewStyles.PAGE_BGCOLOR
        self.__navigation_drawer.attach_to_page(page)

        if bool(getattr(page, "web", False)):
            return

        page.window.width = AppViewStyles.MOBILE_WINDOW_WIDTH
        page.window.height = AppViewStyles.MOBILE_WINDOW_HEIGHT
        page.window.min_width = AppViewStyles.MOBILE_WINDOW_WIDTH
        page.window.min_height = AppViewStyles.MOBILE_WINDOW_HEIGHT
        page.window.resizable = False

    def __resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM

    def __open_navigation_drawer(self, _: ft.Event[ft.IconButton]) -> None:
        try:
            page = self.__root.page
        except RuntimeError:
            return
        if not page:
            return
        self.__navigation_drawer.open(page)

    def __handle_user_settings(self) -> None:
        if self.__on_user_settings:
            self.__on_user_settings()

    def __handle_refresh(self, _: ft.Event[ft.IconButton]) -> None:
        if self.__on_refresh:
            self.__on_refresh()

    def __handle_logout(self) -> None:
        if self.__on_logout:
            self.__on_logout()
