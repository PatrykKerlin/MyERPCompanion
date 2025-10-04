from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import TabsState
from views.base.base_view import BaseView
from views.components.tabs_bar_component import TabsBarComponent
from events.events import TabsBarRequested

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[TabsBarComponent, TabsBarRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        # self.__current_tab: str = ""
        # self.__tabs: dict[str, BaseView] = {}
        self._subscribe_event_handlers({TabsBarRequested: self._component_requested_handler})
        self._subscribe_state_listeners({"tabs": self.__tabs_updated_listener})

    async def _component_requested_handler(self, _: TabsBarRequested) -> None:
        translation_state = self._state_store.app_state.translation
        tabs_state = self._state_store.app_state.tabs
        self._component = TabsBarComponent(
            controller=self,
            translation=translation_state.items,
            tabs=list(tabs_state.items.keys()),
            active_tab=tabs_state.current,
        )
        self._state_store.update(components={"tabs_bar": self._component})

    def __tabs_updated_listener(self, state: TabsState) -> None:
        if not self._component:
            return
        self._component.active_tab = state.current
        self._component.tabs = list(state.items.keys())
        self._component.refresh()

    # @property
    # def current_tab(self) -> str:
    #     return self.__current_tab

    # def add_tab(self, key: str) -> None:
    #     if key not in self._context.active_views:
    #         return
    #     if key not in self.__tabs:
    #         self.__tabs.append(key)
    #         self._context.active_views[key].visible = True
    #     self.on_tab_open(key)

    # def on_tab_open(self, key: str) -> None:
    #     self.__active_view_key = key
    #     self.__refresh()
    #     for key, view in self._context.active_views.items():
    #         view.set_visible(key == self.__active_view_key)
    #     active_view = self._context.active_views[self.__active_view_key]
    #     view_controller = self._context.controllers.get_view_controller(active_view.controller_key)
    #     view_controller.set_view(active_view)
    #     self._context.controllers.get("toolbar").refresh()
    #     self._context.page.update()

    # def on_tab_close(self, key: str | None = None) -> None:
    #     if key and key not in self.__tabs:
    #         return
    #     if not key:
    #         key = self.__active_view_key
    #     self.__tabs.remove(key)
    #     old_view = self._context.active_views.pop(key, None)
    #     if old_view:
    #         view_controller = self._context.controllers.get_view_controller(old_view.controller_key)
    #         view_controller.set_view(None)
    #         view_stack = self._context.controllers.get("app").view_stack
    #         self._remove_control(view_stack, old_view)
    #     if self.__tabs:
    #         self.__active_view_key = self.__tabs[-1]
    #         new_view = self._context.active_views[self.__active_view_key]
    #         new_view_controller = self._context.controllers.get_view_controller(new_view.controller_key)
    #         new_view_controller.set_view(new_view)
    #     else:
    #         self.__active_view_key = ""
    #     self.__refresh()
    #     for key, view in self._context.active_views.items():
    #         view.set_visible(key == self.__active_view_key)
    #     self._context.controllers.get("toolbar").refresh()
    #     self._context.page.update()

    # def __refresh(self) -> None:
    #     if self.__tabs_bar:
    #         self.__tabs_bar.tabs = self.__tabs
    #         self.__tabs_bar.active_tab = self.__active_view_key
    #         self.__tabs_bar.refresh()
