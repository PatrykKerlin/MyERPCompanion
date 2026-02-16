import flet as ft
from styles.colors import AppColors
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles
from utils.translation import Translation
from views.base.base_view import BaseView
from views.components.footer_component import FooterComponent
from views.components.menu_bar_component import MenuBarComponent
from views.components.side_menu_component import SideMenuComponent
from views.components.tabs_bar_component import TabsBarComponent
from views.components.toolbar_component import ToolbarComponent


class AppView:
    def __init__(self, translation: Translation, theme: str) -> None:

        self.__theme = theme
        self.__translation = translation
        self.__is_toolbar_visible = True
        self.__is_tabs_bar_visible = True
        self.__menu_bar_container = ft.Container(visible=False)
        self.__menu_toolbar_divider = ft.Divider(
            visible=False,
            height=1,
            thickness=1,
            color=AppColors.OUTLINE,
        )
        self.__toolbar_container = ft.Container(
            visible=False,
            height=AppDimensions.CONTROL_HEIGHT,
            opacity=1.0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            animate=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_size=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_opacity=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
        )
        self.__toolbar_bottom_divider = ft.Divider(
            visible=False,
            height=1,
            thickness=1,
            color=AppColors.OUTLINE,
        )
        self.__side_menu_container = ft.Container(visible=False)
        self.__footer_top_divider = ft.Divider(
            visible=True,
            height=1,
            thickness=1,
            color=AppColors.OUTLINE,
        )
        self.__footer_container = ft.Container(visible=False)
        self.__tabs_bar_container = ft.Container(
            visible=False,
            height=AppDimensions.CONTROL_HEIGHT,
            opacity=1.0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            animate=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_size=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
            animate_opacity=AppDimensions.SHELL_TOGGLE_ANIMATION_MS,
        )
        self.__views_stack = ft.Stack(expand=True, fit=ft.StackFit.EXPAND)
        self.__auth_container = ft.Container(visible=False, expand=True)
        self.__content = ft.Column(
            controls=[
                self.__menu_bar_container,
                self.__menu_toolbar_divider,
                self.__toolbar_container,
                self.__toolbar_bottom_divider,
                ft.Row(
                    controls=[
                        self.__side_menu_container,
                        ft.Column(
                            controls=[
                                self.__tabs_bar_container,
                                self.__views_stack,
                            ],
                            expand=True,
                        ),
                    ],
                    expand=True,
                ),
                self.__footer_top_divider,
                self.__footer_container,
            ],
            alignment=AlignmentStyles.AXIS_START,
            horizontal_alignment=AlignmentStyles.CROSS_STRETCH,
            expand=True,
            visible=False,
        )
        self.__root = ft.Stack(
            controls=[self.__content, self.__auth_container],
            expand=True,
        )

    def build(self) -> ft.Control:
        page = ft.context.page
        self.__apply_page_settings(page)
        return self.__root

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation

    def set_menu_bar(self, component: MenuBarComponent) -> None:
        self.__menu_bar_container.content = component
        self.__menu_bar_container.visible = True
        self.__update_shell_dividers()

    def set_toolbar(self, component: ToolbarComponent) -> None:
        self.__toolbar_container.content = component
        self.__apply_toolbar_visibility()
        self.__update_shell_dividers()

    def set_side_menu(self, component: SideMenuComponent) -> None:
        self.__side_menu_container.content = component
        self.__side_menu_container.visible = True

    def set_footer(self, component: FooterComponent) -> None:
        self.__footer_container.content = component
        self.__footer_container.visible = True

    def set_tabs_bar(self, component: TabsBarComponent) -> None:
        self.__tabs_bar_container.content = component
        self.__apply_tabs_bar_visibility()

    def set_auth_view(self, component: ft.Control | None) -> None:
        self.__auth_container.content = component
        self.__auth_container.visible = component is not None

    def set_shell_visible(self, visible: bool) -> None:
        self.__content.visible = visible
        if self.__content.page:
            self.__content.update()

    def set_theme(self, theme: str) -> None:
        self.__theme = theme
        page = self.__root.page
        if not page:
            return
        page.theme_mode = self.__resolve_theme_mode(theme)
        page.update()

    def toggle_toolbar_visible(self) -> None:
        self.__is_toolbar_visible = not self.__is_toolbar_visible
        self.__apply_toolbar_visibility()
        self.__update_shell_dividers()

    def toggle_tabs_bar_visible(self) -> None:
        self.__is_tabs_bar_visible = not self.__is_tabs_bar_visible
        self.__apply_tabs_bar_visibility()

    def set_stack_item(self, view: BaseView | None) -> None:
        if view is None:
            for stack_view in self.__views_stack.controls:
                stack_view.visible = False
        else:
            if view not in self.__views_stack.controls:
                self.__views_stack.controls.append(view)
            for stack_view in self.__views_stack.controls:
                stack_view.visible = stack_view is view

    def remove_stack_item(self, view: BaseView) -> None:
        self.__views_stack.controls.remove(view)

    def __apply_page_settings(self, page: ft.Page) -> None:
        page.title = self.__translation.get("my_erp_companion")
        page.theme_mode = self.__resolve_theme_mode(self.__theme)
        page.window.width = AppDimensions.DESKTOP_WINDOW_WIDTH
        page.window.height = AppDimensions.DESKTOP_WINDOW_HEIGHT
        page.window.min_width = AppDimensions.DESKTOP_WINDOW_MIN_WIDTH
        page.window.min_height = AppDimensions.DESKTOP_WINDOW_MIN_HEIGHT

    def __resolve_theme_mode(self, theme: str) -> ft.ThemeMode:
        if theme == "dark":
            return ft.ThemeMode.DARK
        if theme == "light":
            return ft.ThemeMode.LIGHT
        return ft.ThemeMode.SYSTEM

    def __update_shell_dividers(self) -> None:
        has_menu = self.__menu_bar_container.visible and self.__menu_bar_container.content is not None
        has_toolbar = self.__is_toolbar_visible and self.__toolbar_container.content is not None
        self.__menu_toolbar_divider.visible = has_menu
        self.__toolbar_bottom_divider.visible = has_toolbar

    def __apply_toolbar_visibility(self) -> None:
        has_toolbar_component = self.__toolbar_container.content is not None
        self.__toolbar_container.visible = has_toolbar_component
        if not has_toolbar_component:
            return
        if self.__is_toolbar_visible:
            self.__toolbar_container.height = AppDimensions.CONTROL_HEIGHT
        else:
            self.__toolbar_container.height = 0

    def __apply_tabs_bar_visibility(self) -> None:
        has_tabs_bar_component = self.__tabs_bar_container.content is not None
        self.__tabs_bar_container.visible = has_tabs_bar_component
        if not has_tabs_bar_component:
            return
        if self.__is_tabs_bar_visible:
            self.__tabs_bar_container.height = AppDimensions.CONTROL_HEIGHT
        else:
            self.__tabs_bar_container.height = 0
