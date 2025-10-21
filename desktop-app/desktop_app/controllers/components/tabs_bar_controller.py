from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import TabsState
from utils.enums import ViewMode
from views.components.tabs_bar_component import TabsBarComponent
from events.events import TabClosed, TabCloseRequested, TabsBarRequested, TabRequested, ViewReady, ViewRequested

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[TabsBarComponent, TabsBarRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                TabsBarRequested: self._component_requested_handler,
                TabRequested: self.__tab_requested_handler,
                TabCloseRequested: self.__tab_close_requested_handler,
                ViewReady: self.__view_ready_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "tabs": self.__tabs_updated_listener,
            }
        )

    def on_close_clicked(self, title: str) -> None:
        self._page.run_task(self.__execute_close_clicked, title)

    def on_tab_clicked(self, title: str) -> None:
        tabs_state = self._state_store.app_state.tabs
        self._state_store.update(tabs={"current": title, "mode": tabs_state.items[title].mode})

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

    async def __execute_close_clicked(self, title: str) -> None:
        tabs_state = self._state_store.app_state.tabs
        view_key = tabs_state.items[title].view_key
        mode = tabs_state.items[title].mode
        updated_tabs = {key: val for key, val in tabs_state.items.items() if key != title}
        last_tab_title = next(reversed(updated_tabs), "")
        await self._run_with_delay(
            lambda: self._state_store.update(
                tabs={
                    "current": last_tab_title,
                    "mode": updated_tabs[last_tab_title].mode if last_tab_title else ViewMode.SEARCH,
                    "items": updated_tabs,
                }
            )
        )
        if view_key and mode in {ViewMode.SEARCH, ViewMode.LIST}:
            await self._event_bus.publish(TabClosed(view_key=view_key))

    async def __tab_requested_handler(self, event: TabRequested) -> None:
        tabs_state = self._state_store.app_state.tabs
        tab_title = self._get_tab_title(event.view_key, event.postfix)
        if tab_title not in tabs_state.items.keys() or event.replace:
            self._page.run_task(
                self._event_bus.publish,
                ViewRequested(
                    module_id=event.module_id, view_key=event.view_key, postfix=event.postfix, data=event.data
                ),
            )
        else:
            self._state_store.update(tabs={"current": tab_title, "mode": tabs_state.items[tab_title].mode})

    async def __view_ready_handler(self, event: ViewReady) -> None:
        tabs_state = self._state_store.app_state.tabs
        tab_title = self._get_tab_title(event.view_key, event.postfix)
        if tab_title not in tabs_state.items.keys():
            self._state_store.update(
                tabs={
                    "current": tab_title,
                    "mode": event.view.mode,
                    "items": {**tabs_state.items, tab_title: event.view},
                }
            )
        else:
            self._state_store.update(tabs={"current": tab_title, "mode": tabs_state.items[tab_title].mode})

    async def __tab_close_requested_handler(self, event: TabCloseRequested) -> None:
        await self.__execute_close_clicked(event.title)

    def __tabs_updated_listener(self, state: TabsState) -> None:
        if not self._component:
            return
        self._component.active_tab = state.current
        self._component.tabs = list(state.items.keys())
        self._component.refresh()
