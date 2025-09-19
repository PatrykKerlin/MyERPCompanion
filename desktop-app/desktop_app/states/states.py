from __future__ import annotations

from config.translation import Translation

from states.base.base_state import BaseState


class TranslationState(BaseState):
    language: str
    items: dict[str, str]
    success: bool

    @classmethod
    def with_defaults(cls, language: str) -> TranslationState:
        defaults = Translation().defaults
        return cls(language=language, items=defaults, success=True)


class TokenState(BaseState):
    access: str | None = None
    refresh: str | None = None


class AppState(BaseState):
    translation: TranslationState
    token: TokenState
