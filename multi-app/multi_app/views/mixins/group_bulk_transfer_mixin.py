from __future__ import annotations

from typing import Callable, TYPE_CHECKING

import flet as ft

from utils.enums import ViewMode
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from utils.translation import Translation


class GroupBulkTransferMixin:
    _translation: Translation
    _group_bulk_transfer: BulkTransfer
    _group_pending_source_rows: list[tuple[int, list[str]]]
    _group_pending_target_rows: list[tuple[int, list[str]]]
    _group_visible_modes: set[ViewMode]

    def _init_group_bulk_transfer(
        self,
        mode: ViewMode,
        source_rows: list[tuple[int, list[str]]],
        target_rows: list[tuple[int, list[str]]],
        source_label: str,
        target_label: str,
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_delete_clicked: Callable[[list[int]], None] | None = None,
        on_move_requested: Callable[[list[int]], None] | None = None,
        height: int | None = 250,
        visible_modes: set[ViewMode] | None = None,
        target_columns: list[str] | None = None,
    ) -> None:
        self._group_visible_modes = visible_modes or {ViewMode.READ, ViewMode.EDIT}
        self._group_bulk_transfer = BulkTransfer(
            on_save_clicked=on_save_clicked or (lambda _: None),
            source_label=source_label,
            target_label=target_label,
            on_delete_clicked=on_delete_clicked,
            on_move_requested=on_move_requested,
            source_columns=[
                self._translation.get("key"),
                self._translation.get("description"),
            ],
            target_columns=target_columns
            or [
                self._translation.get("key"),
                self._translation.get("description"),
            ],
            height=height,
        )
        self._group_pending_source_rows = source_rows
        self._group_pending_target_rows = target_rows
        self._group_bulk_transfer.visible = mode in self._group_visible_modes
        self._set_group_bulk_transfer_state(mode)

    def _build_group_bulk_transfer_row(self) -> ft.Row:
        return ft.Row(controls=[ft.Container(content=self._group_bulk_transfer, expand=True)])

    def _mount_group_bulk_transfer(self) -> None:
        self._group_bulk_transfer.set_source_rows(self._group_pending_source_rows)
        self._group_bulk_transfer.set_target_rows(self._group_pending_target_rows)

    def _update_group_bulk_transfer_mode(self, mode: ViewMode) -> None:
        self._group_bulk_transfer.visible = mode in self._group_visible_modes
        self._set_group_bulk_transfer_state(mode)
        self._group_bulk_transfer.clear_pending_changes()

    def _set_group_bulk_transfer_state(self, mode: ViewMode) -> None:
        editable = mode == ViewMode.READ
        self._group_bulk_transfer.set_enabled_states(editable, editable, editable)

    def get_pending_group_targets(self) -> list[tuple[int, int]]:
        return self._group_bulk_transfer.get_pending_targets()

    def set_group_source_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self._group_bulk_transfer.set_source_rows(rows)

    def set_group_target_rows(self, rows: list[tuple[int, list[str]]]) -> None:
        self._group_bulk_transfer.set_target_rows(rows)
