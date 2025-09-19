from dataclasses import dataclass

from events.base.base_event import BaseEvent


@dataclass(frozen=True)
class AppStarted(BaseEvent):
    pass


@dataclass(frozen=True)
class ApiReady(BaseEvent):
    pass


@dataclass(frozen=True)
class ApiNotResponding(BaseEvent):
    pass


@dataclass(frozen=True)
class TranslationRequested(BaseEvent):
    language: str


@dataclass(frozen=True)
class TranslationLoaded(BaseEvent):
    language: str
    items: dict[str, str]


@dataclass(frozen=True)
class TranslationFailed(BaseEvent):
    language: str


@dataclass(frozen=True)
class TranslationReady(BaseEvent):
    pass
