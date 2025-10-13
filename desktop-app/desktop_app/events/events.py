from __future__ import annotations

from typing import Any

from dataclasses import dataclass

from events.base.base_event import BaseEvent
from views.base.base_view import BaseView


@dataclass(frozen=True)
class AppStarted(BaseEvent):
    pass


@dataclass(frozen=True)
class ApiStatusRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ApiStatusChecked(BaseEvent):
    status: bool


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
class UserAuthenticated(BaseEvent):
    pass


@dataclass(frozen=True)
class SideMenuRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class SideMenuToggleRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ToolbarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabsBarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class FooterRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class FooterMounted(BaseEvent):
    pass


@dataclass(frozen=True)
class MenuBarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ViewRequested(BaseEvent):
    key: str
    postfix: int | None = None
    data: dict[str, Any] | None = None


@dataclass(frozen=True)
class ViewReady(BaseEvent):
    key: str
    view: BaseView
    postfix: int | None = None


@dataclass(frozen=True)
class TabRequested(BaseEvent):
    key: str
    postfix: int | None = None
    data: dict[str, Any] | None = None
    replace: bool = False


@dataclass(frozen=True)
class TabCloseRequested(BaseEvent):
    title: str


@dataclass(frozen=True)
class TabClosed(BaseEvent):
    key: str


@dataclass(frozen=True)
class RecordDeleteRequested(BaseEvent):
    key: str
    id: int
