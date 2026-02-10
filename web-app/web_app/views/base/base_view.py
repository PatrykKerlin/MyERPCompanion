from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Sequence, TypeVar

import flet as ft

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseView(BaseComponent, Generic[TController], ft.Container):
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
        del base_label_size, base_input_size, base_columns_qty
        BaseComponent.__init__(self, controller, translation)
        self._mode = mode
        self._view_key = view_key
        self._data_row = data_row
        self._inputs: dict[str, FieldGroup] = {}
        self._caller_view_key = caller_view_key
        ft.Container.__init__(self, content=None, expand=True)

    @property
    def caller_view_key(self) -> View | None:
        return self._caller_view_key

    @property
    def data_row(self) -> dict[str, Any] | None:
        return self._data_row

    @property
    def inputs(self) -> dict[str, FieldGroup]:
        return self._inputs

    @property
    def mode(self) -> ViewMode:
        return self._mode

    @property
    def view_key(self) -> View:
        return self._view_key

    def set_mode(self, mode: ViewMode) -> None:
        self._mode = mode

    def _get_dropdown(
        self,
        key: str,
        size: int,
        options: Sequence[tuple[int | str, str]],
        callbacks: list[Callable[..., None]] | None = None,
    ) -> tuple[ft.Container, int]:
        def handle_select(_: ft.ControlEvent) -> None:
            for callback in callbacks or []:
                callback()

        return (
            ft.Container(
                content=ft.Dropdown(
                    options=[ft.dropdown.Option(key="0", text="")]
                    + [ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in options],
                    on_select=handle_select,
                    expand=True,
                    value="0",
                    editable=True,
                    enable_search=True,
                    enable_filter=True,
                ),
                col={"sm": float(size)},
                alignment=ft.Alignment.CENTER_LEFT,
            ),
            size,
        )
