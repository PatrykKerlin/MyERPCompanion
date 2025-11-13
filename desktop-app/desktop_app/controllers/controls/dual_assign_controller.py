from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from views.controls.dual_assign_control import DualAssign


class DualAssignController:
    def __init__(self) -> None:
        self.__control: DualAssign | None = None

    def attach_control(self, control: DualAssign) -> None:
        self.__control = control

    def detach_control(self) -> None:
        self.__control = None

    def on_move_clicked(self, _: ft.ControlEvent | None = None) -> None:
        if not self.__control:
            return
        selected_ids = self.__control.get_selected_source_ids()
        if not selected_ids:
            return
        items_to_move = self.__control.get_source_items_by_ids(selected_ids)
        if not items_to_move:
            return
        self.__control.prepend_target_items(items_to_move, highlight=True)
        self.__control.remove_source_items(selected_ids)

    def on_delete_clicked(self, _: ft.ControlEvent | None = None) -> None:
        if not self.__control:
            return
        return
