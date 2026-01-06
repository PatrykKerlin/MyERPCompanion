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
        ids_to_add = [item_id for item_id in selected_ids if not self.__control.has_target_item(item_id)]
        if not ids_to_add:
            return
        items_to_move = self.__control.get_source_items_by_ids(ids_to_add)
        if not items_to_move:
            return
        actual_ids = [item_id for item_id, _ in items_to_move]
        if not actual_ids:
            return
        self.__control.mark_source_items_as_moved(actual_ids)
        self.__control.prepend_target_items(items_to_move, highlight=True)

    def on_delete_clicked(self, _: ft.ControlEvent | None = None) -> None:
        if not self.__control:
            return
        selected_ids = self.__control.get_selected_target_ids()
        if not selected_ids:
            return
        deletable_ids = [item_id for item_id in selected_ids if self.__control.is_target_item_from_source(item_id)]
        if not deletable_ids:
            return
        self.__control.remove_target_items(deletable_ids)

    def get_pending_move_ids(self) -> list[int]:
        if not self.__control:
            return []
        return self.__control.get_pending_move_ids()
