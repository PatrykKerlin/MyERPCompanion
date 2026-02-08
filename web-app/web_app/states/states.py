from schemas.core.module_schema import ModulePlainSchema
from schemas.core.user_schema import UserPlainSchema
from states.base.base_state import BaseState

from utils.enums import ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

import flet as ft


class TranslationState(BaseState):
    language: str
    items: Translation


class TokensState(BaseState):
    access: str | None = None
    refresh: str | None = None


class UserState(BaseState):
    current: UserPlainSchema | None = None


class ModulesState(BaseState):
    items: list[ModulePlainSchema]


class ViewState(BaseState):
    title: str
    mode: ViewMode
    view: BaseView | None


class AppState(BaseState):
    translation: TranslationState
    tokens: TokensState
    user: UserState
    modules: ModulesState
    view: ViewState


ViewState.model_rebuild(force=True, _types_namespace={"Control": ft.Control, "Theme": ft.Theme})
