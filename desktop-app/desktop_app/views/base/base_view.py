from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

import customtkinter as ctk

if TYPE_CHECKING:
    from controllers.base import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseView(ABC, Generic[TController]):
    def __init__(self, master: ctk.CTk, controller: TController, texts: dict[str, str]) -> None:
        self._master = master
        self._controller = controller
        self._texts = texts

    @abstractmethod
    def _build(self) -> None:
        pass

    @abstractmethod
    def show(self, *args, **kwargs) -> None:
        pass
