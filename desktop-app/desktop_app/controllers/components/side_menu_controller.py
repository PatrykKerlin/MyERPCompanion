from __future__ import annotations

from typing import TYPE_CHECKING, Any

from controllers.base.base_component_controller import BaseComponentController
from views.base.base_view import BaseView
from views.components.side_menu_component import SideMenuComponent
from events.events import SideMenuRequested, SideMenuToggleRequested, TabRequested, ViewReady

if TYPE_CHECKING:
    from config.context import Context


class SideMenuController(BaseComponentController[SideMenuComponent, SideMenuRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__is_component_visible = True
        self.__component_width: float | None = None
        self._subscribe_event_handlers(
            {
                SideMenuRequested: self._component_requested_handler,
                SideMenuToggleRequested: self.__toggle_handler,
            }
        )

    def on_item_clicked(self, key: str) -> None:
        self._page.run_task(self._event_bus.publish, TabRequested(key=key))

    async def _component_requested_handler(self, _: SideMenuRequested) -> None:
        translation_state = self._state_store.app_state.translation
        modules_state = self._state_store.app_state.modules
        content: dict[str, list[str]] = {}
        if modules_state.items:
            sorted_modules = sorted(modules_state.items, key=lambda module: module.order)
            for module in sorted_modules:
                if module.key == "core":
                    continue
                content[module.key] = [view.key for view in module.views]
        self._component = SideMenuComponent(controller=self, translation=translation_state.items, content=content)
        self._state_store.update(components={"side_menu": self._component})
        self.__is_component_visible = True
        self.__component_width = None

    async def __toggle_handler(self, _: SideMenuToggleRequested) -> None:
        if not self._component:
            return
        if not self.__component_width:
            self.__component_width = self._component.width
        self.__is_component_visible = not self.__is_component_visible
        self._component.width = self.__component_width if self.__is_component_visible else 0
        self._component.opacity = 1.0 if self.__is_component_visible else 0.0
        self._page.update()
