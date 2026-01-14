from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from controllers.business.logistic.bin_transfer_controller import BinTransferController


class BinTransferView(BaseView):
    def __init__(
        self,
        controller: BinTransferController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        on_source_submitted: Callable[[ft.Event[ft.TextField]], None],
        on_target_submitted: Callable[[ft.Event[ft.TextField]], None],
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None],
    ) -> None:
        super().__init__(controller, translation, mode, key, None, 0, 12)
        self._master_column.scroll = None

        self.__source_input = ft.TextField(label=self._translation.get("source_bin"), on_submit=on_source_submitted)
        self.__target_input = ft.TextField(label=self._translation.get("target_bin"), on_submit=on_target_submitted)

        self.__bulk_transfer = BulkTransfer(on_save_clicked=on_save_clicked)

        inputs_row = ft.Row(
            controls=[
                ft.Container(content=self.__source_input, expand=True),
                ft.Container(expand=True),
                ft.Container(content=self.__target_input, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self._master_column.controls = [inputs_row, self.__bulk_transfer]
        self.content = ft.Container(content=self._master_column, expand=True)

    def get_pending_move_ids(self) -> list[int]:
        return self.__bulk_transfer.get_pending_move_ids()

    def set_source_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_source_enabled(enabled)

    def set_target_enabled(self, enabled: bool) -> None:
        self.__bulk_transfer.set_target_enabled(enabled)

    def set_source_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_source_items(items)

    def set_target_items(self, items: list[tuple[int, str]]) -> None:
        self.__bulk_transfer.set_target_items(items)

    def prepend_target_items(self, items: list[tuple[int, str]], highlight: bool) -> None:
        self.__bulk_transfer.prepend_target_items(items, highlight)

    def remove_source_items(self, ids: list[int]) -> None:
        self.__bulk_transfer.remove_source_items(ids)

    def get_selected_source_ids(self) -> list[int]:
        return self.__bulk_transfer.get_selected_source_ids()

    def set_source_error(self, message: str | None) -> None:
        self.__source_input.error = message
        self.update()

    def set_target_error(self, message: str | None) -> None:
        self.__target_input.error = message
        self.update()
