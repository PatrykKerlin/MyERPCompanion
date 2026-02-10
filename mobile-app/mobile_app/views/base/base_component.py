from __future__ import annotations

from typing import Generic, TypeVar, TYPE_CHECKING
from controllers.base.base_controller import BaseController

if TYPE_CHECKING:
    from utils.translation import Translation

TController = TypeVar("TController", bound=BaseController)


class BaseComponent(Generic[TController]):
    def __init__(self, controller: TController, translation: Translation) -> None:
        self._controller = controller
        self._translation = translation
