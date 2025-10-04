from dataclasses import dataclass

from events.base.base_event import BaseEvent


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
