from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import flet as ft
from controllers.base.base_controller import BaseController
from views.mixins.input_controls_mixin import InputControlsMixin

if TYPE_CHECKING:
    from utils.translation import Translation

TController = TypeVar("TController", bound=BaseController)


class BaseComponent(InputControlsMixin, Generic[TController]):
    def __init__(self, controller: TController, translation: Translation) -> None:
        self._controller = controller
        self._translation = translation

    @staticmethod
    def safe_update(control: ft.Control | None) -> None:
        if control is None:
            return
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
