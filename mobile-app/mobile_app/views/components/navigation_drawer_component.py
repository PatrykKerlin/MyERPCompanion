from __future__ import annotations

from collections.abc import Awaitable, Callable

import flet as ft
from styles.styles import AppViewStyles, TypographyStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.mixins.input_controls_mixin import InputControlsMixin


class NavigationDrawerComponent(InputControlsMixin):
    __MENU_ITEMS: list[tuple[View, str]] = [
        (View.BINS, "bins"),
        (View.ITEMS, "items"),
        (View.BIN_TRANSFER, "bin_transfer"),
        (View.ORDER_PICKING, "order_picking"),
        (View.STOCK_RECEIVING, "stock_receiving"),
    ]

    def __init__(self, translation: Translation) -> None:
        self.__translation = translation
        self.__on_view_selected: Callable[[View], None] | None = None
        self.__drawer_views: list[View] = []
        self.__current_warehouse_name: str | None = None
        self.__drawer = ft.NavigationDrawer(controls=[], on_change=self.__on_drawer_change)
        self.__refresh_controls()

    @property
    def drawer(self) -> ft.NavigationDrawer:
        return self.__drawer

    def update_translation(self, translation: Translation) -> None:
        self.__translation = translation
        self.__refresh_controls()

    def set_navigation_handler(self, on_view_selected: Callable[[View], None]) -> None:
        self.__on_view_selected = on_view_selected
        self.__refresh_controls()

    def set_warehouse_name(self, warehouse_name: str | None) -> None:
        self.__current_warehouse_name = warehouse_name
        self.__refresh_controls()

    def attach_to_page(self, page: ft.Page | ft.BasePage) -> None:
        page.drawer = self.__drawer

    def open(self, page: ft.Page | ft.BasePage) -> None:
        page.drawer = self.__drawer
        self.__run_task(page, self.__show_drawer)

    def __refresh_controls(self) -> None:
        self.__drawer_views = []
        title_controls: list[ft.Control] = [
            self._get_label(self.__translation.get("my_erp_companion"), style=TypographyStyles.SECTION_TITLE)
        ]
        if self.__current_warehouse_name:
            title_controls.append(
                self._get_label(
                    self.__current_warehouse_name,
                    size=AppViewStyles.DRAWER_SUBTITLE_SIZE,
                    color=AppViewStyles.DRAWER_SUBTITLE_COLOR,
                )
            )
        controls: list[ft.Control] = [
            ft.Container(
                padding=AppViewStyles.DRAWER_HEADER_PADDING,
                content=ft.Column(controls=title_controls, spacing=AppViewStyles.DRAWER_HEADER_SPACING, tight=True),
            ),
            ft.Divider(height=AppViewStyles.DRAWER_DIVIDER_HEIGHT),
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
        BaseComponent.safe_update(self.__drawer)

    def __on_drawer_change(self, _: ft.Event[ft.NavigationDrawer]) -> None:
        index = self.__drawer.selected_index
        if not isinstance(index, int):
            return
        if index < 0 or index >= len(self.__drawer_views):
            return
        selected_view = self.__drawer_views[index]
        if self.__on_view_selected:
            self.__on_view_selected(selected_view)

        page = self.__resolve_page(self.__drawer)
        if page:
            self.__run_task(page, self.__close_drawer)

    @staticmethod
    def __resolve_page(control: ft.Control) -> ft.Page | ft.BasePage | None:
        try:
            return control.page
        except RuntimeError:
            return None

    @staticmethod
    def __run_task(
        page: ft.Page | ft.BasePage,
        task: Callable[[ft.Page | ft.BasePage], Awaitable[None]],
    ) -> None:
        if not isinstance(page, ft.Page):
            return
        page.run_task(task, page)

    @staticmethod
    async def __show_drawer(page: ft.Page | ft.BasePage) -> None:
        await page.show_drawer()

    @staticmethod
    async def __close_drawer(page: ft.Page | ft.BasePage) -> None:
        await page.close_drawer()
