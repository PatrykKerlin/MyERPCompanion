from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import flet as ft
from utils.enums import ViewMode
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from utils.translation import Translation


class DiscountBulkTransferMixin:
    _translation: Translation
    _discount_bulk_transfer: BulkTransfer
    _discount_pending_source_items: list[tuple[int, str]]
    _discount_pending_target_items: list[tuple[int, str]]
    _discount_visible_modes: set[ViewMode]

    def get_pending_discount_ids(self) -> list[int]:
        return self._discount_bulk_transfer.get_pending_move_ids()

    def set_discount_source_items(self, items: list[tuple[int, str]]) -> None:
        self._discount_bulk_transfer.set_source_items(items)

    def set_discount_target_items(self, items: list[tuple[int, str]]) -> None:
        self._discount_bulk_transfer.set_target_items(items)

    def _init_discount_bulk_transfer(
        self,
        mode: ViewMode,
        source_items: list[tuple[int, str]],
        target_items: list[tuple[int, str]],
        source_label: str,
        target_label: str,
        on_save_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        on_delete_clicked: Callable[[list[int]], None] | None = None,
        height: int | None = 250,
        visible_modes: set[ViewMode] | None = None,
    ) -> None:
        self._discount_visible_modes = visible_modes or {ViewMode.CREATE, ViewMode.EDIT, ViewMode.READ}
        self._discount_bulk_transfer = BulkTransfer(
            on_save_clicked=on_save_clicked or (lambda _: None),
            source_label=source_label,
            target_label=target_label,
            on_delete_clicked=on_delete_clicked,
            source_columns=[self._translation.get("code")],
            target_columns=[self._translation.get("code")],
            height=height,
        )
        self._discount_pending_source_items = source_items
        self._discount_pending_target_items = target_items
        self._discount_bulk_transfer.visible = mode in self._discount_visible_modes
        self._set_discount_bulk_transfer_state(mode)

    def _build_discount_bulk_transfer_row(self) -> ft.Row:
        return ft.Row(controls=[ft.Container(content=self._discount_bulk_transfer, expand=True)])

    def _mount_discount_bulk_transfer(self) -> None:
        self._discount_bulk_transfer.set_source_items(self._discount_pending_source_items)
        self._discount_bulk_transfer.set_target_items(self._discount_pending_target_items)

    def _update_discount_bulk_transfer_mode(self, mode: ViewMode) -> None:
        self._discount_bulk_transfer.visible = mode in self._discount_visible_modes
        self._set_discount_bulk_transfer_state(mode)
        self._discount_bulk_transfer.clear_pending_changes()

    def _set_discount_bulk_transfer_state(self, mode: ViewMode) -> None:
        editable = mode == ViewMode.READ
        self._discount_bulk_transfer.set_enabled_states(editable, editable, editable)
