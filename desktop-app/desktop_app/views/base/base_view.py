from typing import TypeVar, Generic, TYPE_CHECKING
import flet as ft


if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseView(Generic[TController]):
    def __init__(self, controller: TController, texts: dict[str, str]) -> None:
        self._controller = controller
        self._texts = texts
