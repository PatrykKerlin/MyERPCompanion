from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from events.base.base_event import BaseEvent
from utils.enums import View

if TYPE_CHECKING:
    from views.base.base_view import BaseView


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
class MobileMainMenuRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class LogoutRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ViewRequested(BaseEvent):
    module_id: int
    view_key: View
    record_id: int | None = None
    data: dict[str, Any] | None = None
    caller_view_key: View | None = None
    caller_data: dict[str, Any] | None = None
    width_ratio: float = 0.5
    save_succeeded: bool = False


@dataclass(frozen=True)
class ViewReady(BaseEvent):
    view_key: View
    view: BaseView
    record_id: int | None = None
    width_ratio: float = 0.5
    save_succeeded: bool = False
