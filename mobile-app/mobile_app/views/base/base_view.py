from __future__ import annotations

from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

import flet as ft
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from styles.styles import BaseViewStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.controls.numeric_field_control import NumericField

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
        view_key: View,
        caller_view_key: View | None = None,
    ) -> None:
        BaseComponent.__init__(self, controller, translation)
        self._view_key = view_key
        self._inputs: dict[str, ft.Control] = {}
        self._master_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self._caller_view_key = caller_view_key

        ft.Container.__init__(self, content=self._master_column, expand=True)

    @property
    def view_key(self) -> View:
        return self._view_key

    @property
    def inputs(self) -> dict[str, ft.Control]:
        return self._inputs

    @property
    def caller_view_key(self) -> View | None:
        return self._caller_view_key

    @property
    def app_page(self) -> Any:
        return self._controller.page

    def pop_dialog(self) -> Any:
        return self._controller.pop_dialog()

    def queue_dialog(self, dialog: Any, wait_for_future: Awaitable[Any] | None = None) -> None:
        self._controller.enqueue_dialog(dialog, wait_for_future)

    def set_field_error(self, key: str, message: str | None) -> None:
        control = self._inputs[key]
        if isinstance(control, (ft.TextField, NumericField)):
            control.error = message
        elif isinstance(control, ft.Dropdown):
            control.error_text = message
        elif isinstance(control, ft.Checkbox):
            control.error = bool(message)
            control.tooltip = message
        self.safe_update(control)

    def _add_to_inputs(self, *fields: dict[str, ft.Control]) -> None:
        for field in fields:
            self._inputs.update(field)

    @staticmethod
    def _responsive_col(size: int) -> ft.ResponsiveNumber:
        return cast(ft.ResponsiveNumber, {BaseViewStyles.RESPONSIVE_BREAKPOINT: float(size)})
