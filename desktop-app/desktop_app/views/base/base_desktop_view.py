from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import flet as ft
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseDesktopView(BaseView[TController], ft.Card):
    def __init__(
        self,
        controller: TController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        base_label_size: int,
        base_input_size: int,
        base_columns_qty: int = 12,
        caller_view_key: View | None = None,
    ) -> None:
        BaseView.__init__(
            self,
            controller=controller,
            translation=translation,
            mode=mode,
            view_key=view_key,
            data_row=data_row,
            base_label_size=base_label_size,
            base_input_size=base_input_size,
            base_columns_qty=base_columns_qty,
            caller_view_key=caller_view_key,
        )
        self._cancel_button = ft.Button(
            content=self._translation.get("cancel"),
            on_click=lambda _: self._controller.on_cancel_clicked(),
        )
        self._save_button = ft.Button(
            content=self._translation.get("save"),
            on_click=lambda _: self._controller.on_save_clicked(),
            disabled=False,
        )
        self._search_button = ft.Button(
            content=self._translation.get("search"),
            on_click=lambda _: self._controller.on_search_clicked(),
        )
        self._buttons_row = ft.Row(
            controls=[self._search_button, self._cancel_button, self._save_button],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self._rows = [self._columns_row, self._spacing_row, self._buttons_row]
        ft.Card.__init__(self, content=self._base_content, expand=True)

    @property
    def buttons_row(self) -> ft.Row:
        return self._buttons_row

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        self.__set_buttons()

    def __set_buttons(self) -> None:
        if self._mode == ViewMode.STATIC:
            return
        if self._mode in [ViewMode.EDIT, ViewMode.CREATE]:
            self._cancel_button.visible = True
            self._save_button.visible = True
            self._search_button.visible = False
        elif self._mode == ViewMode.SEARCH:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = True
        elif self._mode == ViewMode.READ:
            self._cancel_button.visible = False
            self._save_button.visible = False
            self._search_button.visible = False
        if self._cancel_button.page:
            self._cancel_button.update()
        if self._save_button.page:
            self._save_button.update()
        if self._search_button.page:
            self._search_button.update()
