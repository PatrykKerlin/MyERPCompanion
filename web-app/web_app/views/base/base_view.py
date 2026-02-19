from __future__ import annotations

from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import flet as ft
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService
from utils.enums import View, ViewMode
from utils.field_group import FieldGroup
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.mixins.input_controls_mixin import InputControlsMixin

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController

TController = TypeVar(
    "TController", bound="BaseViewController[BaseService, BaseView, BasePlainSchema, BaseStrictSchema]"
)


class BaseView(BaseComponent, InputControlsMixin, Generic[TController], ft.Container):
    def __init__(
        self,
        controller: TController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        caller_view_key: View | None = None,
    ) -> None:
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
    def mode(self) -> ViewMode:
        return self._mode

    @property
    def view_key(self) -> View:
        return self._view_key

    @property
    def app_page(self) -> Any:
        return self._controller.page

    def pop_dialog(self) -> Any:
        return self._controller.pop_dialog()

    def queue_dialog(self, dialog: Any, wait_for_future: Awaitable[Any] | None = None) -> None:
        self._controller.queue_dialog(dialog, wait_for_future)

    def get_viewport_size(self) -> tuple[int | None, int | None]:
        page = self.app_page
        return page.width or page.window.width, page.height or page.window.height
