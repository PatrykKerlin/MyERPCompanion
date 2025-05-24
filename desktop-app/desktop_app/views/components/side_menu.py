import flet as ft


class SideMenu(ft.NavigationRail):
    def __init__(self, texts: dict[str, str], visible: bool = True) -> None:
        super().__init__(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            visible=visible,
            expand=True,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label=texts["new"],
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label=texts["open"],
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOGOUT,
                    label=texts["about"],
                ),
            ],
        )
        self.visible = visible
