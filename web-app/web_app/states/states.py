import flet as ft
from schemas.core.user_schema import UserPlainSchema
from states.base.base_state import BaseState
from utils.translation import Translation
from views.base.base_view import BaseView


class TranslationState(BaseState):
    language: str
    items: Translation


class TokensState(BaseState):
    access: str | None = None
    refresh: str | None = None


class UserState(BaseState):
    current: UserPlainSchema | None = None


class ViewState(BaseState):
    view: BaseView | None


class AppState(BaseState):
    translation: TranslationState
    tokens: TokensState
    user: UserState
    view: ViewState


ViewState.model_rebuild(force=True, _types_namespace={"Control": ft.Control, "Theme": ft.Theme})
