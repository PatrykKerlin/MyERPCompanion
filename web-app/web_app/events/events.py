from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from events.base.base_event import BaseEvent
from utils.enums import View


@dataclass(frozen=True)
class AppStarted(BaseEvent):
    pass


@dataclass(frozen=True)
class TranslationRequested(BaseEvent):
    language: str
    user_authenticated: bool


@dataclass(frozen=True)
class TranslationReady(BaseEvent):
    user_authenticated: bool


@dataclass(frozen=True)
class TranslationFailed(BaseEvent):
    pass


@dataclass(frozen=True)
class AuthDialogRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class AuthViewReady(BaseEvent):
    component: Any | None


@dataclass(frozen=True)
class UserAuthenticated(BaseEvent):
    pass


@dataclass(frozen=True)
class CartUpdated(BaseEvent):
    count: int


@dataclass(frozen=True)
class LogoutRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ViewRequested(BaseEvent):
    module_id: int
    view_key: View
