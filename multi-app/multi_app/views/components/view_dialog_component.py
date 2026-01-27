import flet as ft

from views.base.base_dialog import BaseDialog


class ViewDialog(BaseDialog):
    def __init__(
        self,
        view: ft.Control,
        title: str,
        width_ratio: float = 0.5,
        actions: list[ft.Control] | None = None,
    ) -> None:
        self.__width_ratio = width_ratio
        self.__content_container = ft.Container(content=view)
        super().__init__(controls=[self.__content_container], actions=actions, title=title)

    def did_mount(self) -> None:
        if not self.page or not self.page.width:
            return
        self.__content_container.width = int(self.page.width * self.__width_ratio)
        self.__content_container.update()
        return super().did_mount()
