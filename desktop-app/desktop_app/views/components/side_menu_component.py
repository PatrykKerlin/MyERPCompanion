from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
from schemas.core import ModuleInputSchema, UserInputSchema
from views.base import BaseView

if TYPE_CHECKING:
    from controllers.components.side_menu_controller import SideMenuController
    from schemas.core.module_schema import ModuleInputSchema
    from schemas.core.user_schema import UserInputSchema


class SideMenuComponent(BaseView, ft.Container):
    def __init__(
        self,
        controller: SideMenuController,
        texts: dict[str, str],
        modules: list[ModuleInputSchema],
        user: UserInputSchema,
        visible: bool,
    ) -> None:
        BaseView.__init__(self, controller, texts)
        self.__modules = modules
        self.__user = user
        self.__labels: list[str] = []
        self.__controls: list[ft.Control] = []
        self.__build_controls()
        self.calculated_width = self.__calculate_width()
        ft.Container.__init__(
            self,
            content=self.__build_content(),
            alignment=ft.alignment.top_center,
            width=self.calculated_width,
            opacity=1.0,
            animate_opacity=300,
            animate_size=300,
            visible=visible,
        )

    def __build_controls(self) -> None:
        user_groups = {group.id for group in self.__user.groups}
        for module in sorted(self.__modules, key=lambda m: m.order):
            module_groups = {group.id for group in module.groups}
            if user_groups.intersection(module_groups):
                self.__add_module_controls(module)

    def __add_module_controls(self, module: ModuleInputSchema) -> None:
        visible_endpoints = sorted(
            [endpoint for endpoint in module.endpoints if endpoint.in_menu], key=lambda e: e.order
        )
        if not visible_endpoints:
            return
        label = self._texts[module.key]
        self.__labels.append(label)
        self.__controls.append(ft.Text(value=label))
        for endpoint in visible_endpoints:
            self.__add_endpoint_controls(endpoint)

    def __add_endpoint_controls(self, endpoint) -> None:
        if not endpoint.get_key and not endpoint.create_key:
            return

        endpoint_label = self._texts[endpoint.key]
        if endpoint_label:
            self.__labels.append(endpoint_label)
            self.__controls.append(ft.Text(value=endpoint_label))

        if endpoint.get_key:
            self.__add_list_tile(
                key=endpoint.get_key,
                icon=ft.Icons.VIEW_LIST,
            )
        if endpoint.create_key:
            self.__add_list_tile(
                key=endpoint.create_key,
                icon=ft.Icons.ADD,
            )

    def __add_list_tile(self, key: str, icon: str) -> None:
        label = self._texts[key]
        self.__labels.append(label)
        self.__controls.append(
            ft.ListTile(
                title=ft.Text(label),
                leading=ft.Icon(name=icon),
                dense=True,
                on_click=lambda _: self._controller.on_menu_click(key),
            )
        )

    def __build_content(self) -> ft.Column:
        return ft.Column(
            controls=self.__controls,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def __calculate_width(self) -> int:
        max_length = max((len(label) for label in self.__labels), default=20)
        return max_length * 9 + 40
