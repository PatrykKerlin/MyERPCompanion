from pydantic import Field

from schemas.core.module_schema import ModulePlainSchema
from schemas.core.user_schema import UserPlainSchema
from states.base.base_state import BaseState
from utils.enums import ViewMode
from views.base.base_view import BaseView
from views.components.side_menu_component import SideMenuComponent
from views.components.toolbar_component import ToolbarComponent
from views.components.tabs_bar_component import TabsBarComponent
from views.components.footer_component import FooterComponent
from views.components.menu_bar_component import MenuBarComponent
from utils.translation import Translation


class ComponentsState(BaseState):
    menu_bar: MenuBarComponent | None = None
    side_menu: SideMenuComponent | None = None
    toolbar: ToolbarComponent | None = None
    tabs_bar: TabsBarComponent | None = None
    footer: FooterComponent | None = None


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


class TabsState(BaseState):
    current: str
    mode: ViewMode
    items: dict[str, BaseView]


class AppState(BaseState):
    translation: TranslationState
    tokens: TokensState
    user: UserState
    modules: ModulesState
    components: ComponentsState
    tabs: TabsState
