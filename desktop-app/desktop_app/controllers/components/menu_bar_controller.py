from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from views.components.menu_bar_component import MenuBarComponent
from events.events import MenuBarRequested, MenuBarReady

if TYPE_CHECKING:
    from config.context import Context


class MenuBarController(BaseComponentController[MenuBarComponent, MenuBarRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers({MenuBarRequested: self._component_requested_handler})

    async def _component_requested_handler(self, _: MenuBarRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = MenuBarComponent(controller=self, translation=translation_state.items)
        await self._event_bus.publish(MenuBarReady(self._component))
