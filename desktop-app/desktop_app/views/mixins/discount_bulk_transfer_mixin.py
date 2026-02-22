from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import flet as ft
from utils.enums import ViewMode
from views.controls.bulk_transfer_control import BulkTransfer

if TYPE_CHECKING:
    from utils.translation import Translation


DiscountTransferItem = tuple[int, str, str, float | None]


class DiscountBulkTransferMixin:
    _translation: Translation
    _discount_bulk_transfer: BulkTransfer
    _discount_pending_source_items: list[DiscountTransferItem]
    _discount_pending_target_items: list[DiscountTransferItem]
    _discount_visible_modes: set[ViewMode]

    def get_pending_discount_ids(self) -> list[int]:
        return self._discount_bulk_transfer.get_pending_move_ids()

    def set_discount_source_items(self, items: list[DiscountTransferItem]) -> None:
        self._discount_bulk_transfer.set_source_rows(self.__build_discount_rows(items))

    def set_discount_target_items(self, items: list[DiscountTransferItem]) -> None:
        self._discount_bulk_transfer.set_target_rows(self.__build_discount_rows(items))

    def _init_discount_bulk_transfer(
        self,
        mode: ViewMode,
        source_items: list[DiscountTransferItem],
        target_items: list[DiscountTransferItem],
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
            source_columns=[
                self._translation.get("code"),
                self._translation.get("name"),
                self._translation.get("percent"),
            ],
            target_columns=[
                self._translation.get("code"),
                self._translation.get("name"),
                self._translation.get("percent"),
            ],
            height=height,
            cancel_label=self._translation.get("cancel"),
            confirm_label=self._translation.get("ok"),
            delete_confirm_title=self._translation.get("confirm"),
            delete_confirm_message=self._translation.get("delete_selected_items_q"),
        )
        self._discount_pending_source_items = source_items
        self._discount_pending_target_items = target_items
        self._discount_bulk_transfer.visible = mode in self._discount_visible_modes
        self._set_discount_bulk_transfer_state(mode)

    def _build_discount_bulk_transfer_row(self) -> ft.Row:
        return ft.Row(controls=[ft.Container(content=self._discount_bulk_transfer, expand=True)])

    def _mount_discount_bulk_transfer(self) -> None:
        self._discount_bulk_transfer.set_source_rows(self.__build_discount_rows(self._discount_pending_source_items))
        self._discount_bulk_transfer.set_target_rows(self.__build_discount_rows(self._discount_pending_target_items))

    def _update_discount_bulk_transfer_mode(self, mode: ViewMode) -> None:
        self._discount_bulk_transfer.visible = mode in self._discount_visible_modes
        self._set_discount_bulk_transfer_state(mode)
        self._discount_bulk_transfer.clear_pending_changes()

    def _set_discount_bulk_transfer_state(self, mode: ViewMode) -> None:
        editable = mode == ViewMode.READ
        self._discount_bulk_transfer.set_enabled_states(editable, editable, editable)

    def __build_discount_rows(self, items: list[DiscountTransferItem]) -> list[tuple[int, list[Any]]]:
        return [(item_id, [code, name, self.__format_percent(percent)]) for item_id, code, name, percent in items]

    @staticmethod
    def __format_percent(percent: float | None) -> str:
        if percent is None:
            return ""
        return f"{percent:g}"
