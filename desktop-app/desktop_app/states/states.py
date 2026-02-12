import flet as ft
from pydantic import Field
from schemas.core.module_schema import ModulePlainSchema
from schemas.core.user_schema import UserPlainSchema
from states.base.base_state import BaseState
from utils.enums import ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView


class ShellState(BaseState):
    is_menu_bar_ready: bool = False
    is_toolbar_ready: bool = False
    is_side_menu_ready: bool = False
    is_footer_ready: bool = False
    is_tabs_bar_ready: bool = False

    @property
    def is_shell_ready(self) -> bool:
        return (
            self.is_menu_bar_ready
            and self.is_toolbar_ready
            and self.is_side_menu_ready
            and self.is_footer_ready
            and self.is_tabs_bar_ready
        )


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
    shell: ShellState = Field(default_factory=ShellState)
    view: ViewState


ViewState.model_rebuild(force=True, _types_namespace={"Control": ft.Control, "Theme": ft.Theme})
