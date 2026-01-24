from __future__ import annotations

from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import ViewState

from utils.enums import ViewMode
from views.base.base_view import BaseView
from views.components.tabs_bar_component import TabsBarComponent
from events.events import (
    TabClosed,
    TabCloseRequested,
    TabsBarReady,
    TabsBarRequested,
    TabRequested,
    ViewReady,
    SaveSucceeded,
    ViewRequested,
)

if TYPE_CHECKING:
    from config.context import Context


class TabsBarController(BaseComponentController[TabsBarComponent, TabsBarRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__active_tabs: dict[str, BaseView] = {}
        self._subscribe_event_handlers(
            {
                TabsBarRequested: self._component_requested_handler,
                TabRequested: self.__tab_requested_handler,
                ViewReady: self.__view_ready_handler,
                TabCloseRequested: self.__tab_close_requested_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "view": self.__view_updated_listener,
            }
        )

    def on_tab_clicked(self, title: str) -> None:
        view = self.__active_tabs[title]
        self._state_store.update(view={"title": title, "mode": view.mode, "view": view})

    def on_close_clicked(self, title: str) -> None:
        self._page.run_task(self.__execute_close_clicked, title)

    async def _component_requested_handler(self, _: TabsBarRequested) -> None:
        translation = self._state_store.app_state.translation.items
        self._component = TabsBarComponent(controller=self, translation=translation)
        await self._event_bus.publish(TabsBarReady(self._component))

    async def __tab_requested_handler(self, event: TabRequested) -> None:
        tab_title = self._get_tab_title(event.view_key, event.record_id)
        if tab_title not in self.__active_tabs or event.save_succeeded:
            self._page.run_task(
                self._event_bus.publish,
                ViewRequested(
                    module_id=event.module_id,
                    view_key=event.view_key,
                    record_id=event.record_id,
                    data=event.record_data,
                    save_succeeded=event.save_succeeded,
                ),
            )
        else:
            view = self.__active_tabs[tab_title]
            self._state_store.update(view={"title": tab_title, "mode": view.mode, "view": view})

    async def __view_ready_handler(self, event: ViewReady) -> None:
        if event.is_dialog:
            return
        tab_title = self._get_tab_title(event.view_key, event.record_id)
        self.__active_tabs[tab_title] = event.view
        self._state_store.update(view={"title": tab_title, "mode": event.view.mode, "view": event.view})
        if event.save_succeeded:
            self._page.run_task(
                self._event_bus.publish,
                SaveSucceeded(view_key=event.view_key),
            )

    async def __tab_close_requested_handler(self, event: TabCloseRequested) -> None:
        await self.__execute_close_clicked(event.title)

    def __view_updated_listener(self, state: ViewState) -> None:
        if not self._component:
            return
        self._component.active_tab = state.title
        self._component.tabs = list(self.__active_tabs.keys())
        self._component.refresh()

    async def __execute_close_clicked(self, title: str) -> None:
        if not self._component:
            return
        closed_view = self.__active_tabs.pop(title)
        prev_title = next(reversed(self.__active_tabs.keys()), "")
        prev_view = self.__active_tabs.get(prev_title, None)
        if prev_view:
            prev_mode = prev_view.mode
        else:
            prev_mode = ViewMode.NONE
        self._component.active_tab = prev_title
        self._component.tabs = list(self.__active_tabs.keys())
        self._component.refresh()
        self._state_store.update(view={"title": prev_title, "mode": prev_mode, "view": prev_view})
        await self._event_bus.publish(TabClosed(closed_view))
        # if view_key and mode in {ViewMode.SEARCH, ViewMode.LIST}:
        #     await self._event_bus.publish(TabClosed(view_key=view_key))
