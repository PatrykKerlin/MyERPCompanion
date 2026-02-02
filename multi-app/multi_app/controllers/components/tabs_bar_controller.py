from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from controllers.base.base_component_controller import BaseComponentController
from states.states import ViewState

from utils.enums import TabNavigationDirection, ViewMode
from views.base.base_view import BaseView
from views.base.base_dialog import BaseDialog
from views.components.tabs_bar_component import TabsBarComponent
from events.events import (
    TabClosed,
    TabCloseRequested,
    TabCloseAllRequested,
    TabCloseOthersRequested,
    TabNavigateRequested,
    TabsBarReady,
    TabsBarRequested,
    TabRequested,
    TabSearchRequested,
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
                TabNavigateRequested: self.__tab_navigate_requested_handler,
                TabSearchRequested: self.__tab_search_requested_handler,
                TabCloseAllRequested: self.__tab_close_all_requested_handler,
                TabCloseOthersRequested: self.__tab_close_others_requested_handler,
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
        if (
            tab_title not in self.__active_tabs
            or event.mode is not None
            or event.record_data is not None
            or event.record_id is not None
            or event.caller_data is not None
        ):
            self._page.run_task(
                self._event_bus.publish,
                ViewRequested(
                    module_id=event.module_id,
                    view_key=event.view_key,
                    record_id=event.record_id,
                    data=event.record_data,
                    mode=event.mode,
                    caller_view_key=event.caller_view_key,
                    caller_data=event.caller_data,
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

    async def __tab_navigate_requested_handler(self, event: TabNavigateRequested) -> None:
        self.__navigate_tabs(event.direction)

    async def __tab_search_requested_handler(self, _: TabSearchRequested) -> None:
        self.__open_tab_search_dialog()

    async def __tab_close_all_requested_handler(self, _: TabCloseAllRequested) -> None:
        await self.__close_all_tabs()

    async def __tab_close_others_requested_handler(self, _: TabCloseOthersRequested) -> None:
        await self.__close_other_tabs()

    def __view_updated_listener(self, state: ViewState) -> None:
        if not self._component:
            return
        self._component.active_tab = state.title
        self._component.tabs = list(self.__active_tabs.keys())
        self._component.refresh()

    def __navigate_tabs(self, direction: TabNavigationDirection) -> None:
        titles = list(self.__active_tabs.keys())
        if not titles:
            return
        active_title = self._state_store.app_state.view.title
        try:
            current_index = titles.index(active_title)
        except ValueError:
            current_index = 0
        if direction == TabNavigationDirection.FIRST:
            target_index = 0
        elif direction == TabNavigationDirection.LAST:
            target_index = len(titles) - 1
        elif direction == TabNavigationDirection.PREVIOUS:
            target_index = max(0, current_index - 1)
        else:
            target_index = min(len(titles) - 1, current_index + 1)
        if target_index == current_index:
            return
        target_title = titles[target_index]
        target_view = self.__active_tabs.get(target_title)
        if not target_view:
            return
        self._state_store.update(view={"title": target_title, "mode": target_view.mode, "view": target_view})

    def __open_tab_search_dialog(self) -> None:
        if not self._page:
            return
        titles = list(self.__active_tabs.keys())
        if not titles:
            return
        translation = self._state_store.app_state.translation.items
        active_title = self._state_store.app_state.view.title
        dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(title) for title in titles],
            value=active_title if active_title in titles else titles[0],
            width=420,
            enable_filter=True,
            enable_search=True,
            editable=True,
        )

        def close_dialog(_: ft.ControlEvent | None = None) -> None:
            self._page.pop_dialog()

        def confirm_dialog(_: ft.ControlEvent | None = None) -> None:
            selected_title = dropdown.value
            if selected_title:
                target_view = self.__active_tabs.get(selected_title)
                if target_view:
                    self._state_store.update(
                        view={"title": selected_title, "mode": target_view.mode, "view": target_view}
                    )
            close_dialog()

        dialog = BaseDialog(
            title=translation.get("Find tab"),
            controls=[dropdown],
            actions=[
                ft.TextButton(translation.get("cancel"), on_click=close_dialog),
                ft.TextButton(translation.get("ok"), on_click=confirm_dialog),
            ],
        )
        self._page.show_dialog(dialog)

    async def __close_all_tabs(self) -> None:
        if not self.__active_tabs:
            return
        closed_views = list(self.__active_tabs.values())
        self.__active_tabs.clear()
        if self._component:
            self._component.active_tab = ""
            self._component.tabs = []
            self._component.refresh()
        self._state_store.update(view={"title": "", "mode": ViewMode.NONE, "view": None})
        for view in closed_views:
            await self._event_bus.publish(TabClosed(view))

    async def __close_other_tabs(self) -> None:
        if not self.__active_tabs:
            return
        active_title = self._state_store.app_state.view.title
        if not active_title or active_title not in self.__active_tabs:
            return
        keep_view = self.__active_tabs[active_title]
        closed_views = [view for title, view in self.__active_tabs.items() if title != active_title]
        self.__active_tabs = {active_title: keep_view}
        if self._component:
            self._component.active_tab = active_title
            self._component.tabs = [active_title]
            self._component.refresh()
        self._state_store.update(view={"title": active_title, "mode": keep_view.mode, "view": keep_view})
        for view in closed_views:
            await self._event_bus.publish(TabClosed(view))

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
