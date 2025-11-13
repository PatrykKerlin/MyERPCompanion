from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import flet as ft

from utils.enums import ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.dual_assign_control import DualAssign

if TYPE_CHECKING:
    from controllers.business.logistic.bin_transfer_controller import BinTransferController


class BinTransferView(BaseView):
    def __init__(
        self,
        controller: BinTransferController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        on_source_submitted: Callable[[ft.ControlEvent], None],
        on_target_submitted: Callable[[ft.ControlEvent], None],
        on_row_clicked: Callable[[], None],
    ) -> None:
        super().__init__(controller, translation, mode, key, None)
        self._master_column.scroll = None
        self.__dual_assign = DualAssign(
            source_label=self._translation.get("source_bin"),
            target_label=self._translation.get("target_bin"),
            on_source_submitted=on_source_submitted,
            on_target_submitted=on_target_submitted,
            on_row_clicked=on_row_clicked,
        )
        self._master_column.controls = [self.__dual_assign]
        ft.Card.__init__(self, content=self._master_column, expand=True)

    def set_source_enabled(self, enabled: bool) -> None:
        self.__dual_assign.set_source_enabled(enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__dual_assign.set_target_enabled(enabled)

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__dual_assign.set_source_items(items)

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__dual_assign.set_target_items(items)

    def prepend_target_items(self, items: list[tuple[int, str]], highlight: bool) -> None:
        self.__dual_assign.prepend_target_items(items, highlight)

    def remove_source_items(self, ids: list[int]) -> None:
        self.__dual_assign.remove_source_items(ids)

    def get_selected_source_ids(self) -> list[int]:
        return self.__dual_assign.get_selected_source_ids()

    def set_source_error(self, message: str | None) -> None:
        self.__dual_assign.set_source_error(message)

    def set_target_error(self, message: str | None) -> None:
        self.__dual_assign.set_target_error(message)
