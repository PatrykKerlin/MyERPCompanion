from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dataclasses import dataclass

from events.base.base_event import BaseEvent
from utils.enums import TabNavigationDirection, View, ViewMode

if TYPE_CHECKING:
    from views.base.base_view import BaseView
    from views.components.footer_component import FooterComponent
    from views.components.menu_bar_component import MenuBarComponent
    from views.components.side_menu_component import SideMenuComponent
    from views.components.tabs_bar_component import TabsBarComponent
    from views.components.toolbar_component import ToolbarComponent


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
class AuthViewReady(BaseEvent):
    component: Any | None


@dataclass(frozen=True)
class UserAuthenticated(BaseEvent):
    pass


@dataclass(frozen=True)
class MobileMainMenuRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class CartUpdated(BaseEvent):
    count: int


@dataclass(frozen=True)
class SideMenuRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class SideMenuReady(BaseEvent):
    component: SideMenuComponent


@dataclass(frozen=True)
class SideMenuToggleRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ToolbarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ToolbarReady(BaseEvent):
    component: ToolbarComponent


@dataclass(frozen=True)
class TabsBarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabsBarReady(BaseEvent):
    component: TabsBarComponent


@dataclass(frozen=True)
class FooterRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class FooterReady(BaseEvent):
    component: FooterComponent


@dataclass(frozen=True)
class MenuBarRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class MenuBarReady(BaseEvent):
    component: MenuBarComponent


@dataclass(frozen=True)
class ToolbarToggleRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class LogoutRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabsBarToggleRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class ViewRequested(BaseEvent):
    module_id: int
    view_key: View
    record_id: int | None = None
    data: dict[str, Any] | None = None
    mode: ViewMode | None = None
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


@dataclass(frozen=True)
class TabRequested(BaseEvent):
    module_id: int
    view_key: View
    record_id: int | None = None
    record_data: dict[str, Any] | None = None
    mode: ViewMode | None = None
    caller_view_key: View | None = None
    caller_data: dict[str, Any] | None = None
    save_succeeded: bool = False


@dataclass(frozen=True)
class CallerActionRequested(BaseEvent):
    caller_view_key: View
    source_view_key: View
    created_id: int
    record_data: dict[str, Any]
    caller_data: dict[str, Any] | None = None


@dataclass(frozen=True)
class TabNavigateRequested(BaseEvent):
    direction: TabNavigationDirection


@dataclass(frozen=True)
class TabSearchRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabCloseAllRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabCloseOthersRequested(BaseEvent):
    pass


@dataclass(frozen=True)
class TabReady(BaseEvent):
    title: str


@dataclass(frozen=True)
class TabCloseRequested(BaseEvent):
    title: str


@dataclass(frozen=True)
class TabClosed(BaseEvent):
    view: BaseView


@dataclass(frozen=True)
class RecordDeleteRequested(BaseEvent):
    view_key: View
    id: int


@dataclass(frozen=True)
class SaveSucceeded(BaseEvent):
    view_key: View
