from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from events.events import SideMenuReady, SideMenuRequested, SideMenuToggleRequested, TabRequested
from utils.enums import View
from views.components.side_menu_component import SideMenuComponent

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

    def on_item_clicked(self, module_id: int, view_key: View) -> None:
        self._page.run_task(self._event_bus.publish, TabRequested(module_id=module_id, view_key=view_key))

    async def _component_requested_handler(self, _: SideMenuRequested) -> None:
        translation = self._state_store.app_state.translation.items
        modules = self._state_store.app_state.modules.items
        content: dict[str, list[tuple[int, str]]] = {}
        if modules:
            sorted_modules = sorted(modules, key=lambda module: module.order)
            for module in sorted_modules:
                if not module.in_side_menu:
                    continue
                content[module.key] = [(module.id, view.key) for view in module.views]
        self._component = SideMenuComponent(controller=self, translation=translation, content=content)
        await self._event_bus.publish(SideMenuReady(self._component))
        self.__is_component_visible = True
        self.__component_width = None

    async def __toggle_handler(self, _: SideMenuToggleRequested) -> None:
        if not self._component:
            return
        if not self.__component_width:
            self.__component_width = self._component.width
        self.__is_component_visible = not self.__is_component_visible
        self._component.set_scroll_enabled(self.__is_component_visible)
        self._component.width = self.__component_width if self.__is_component_visible else 0
        self._page.update()
