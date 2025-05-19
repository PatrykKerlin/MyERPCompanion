import flet as ft
from controllers.core import AppController, AuthController
from config import Context, Settings, Controllers, DefaultTranslation


class App:
    def main(self, page: ft.Page) -> None:
        settings = Settings()  # type: ignore
        self.__controllers = Controllers()
        self.__context = Context(
            settings=settings,
            controllers=self.__controllers,
            page=page,
            texts=DefaultTranslation.texts,
        )
        self.__register_controllers()
        self.__controllers.app.show()

    def __register_controllers(self):
        self.__controllers.add("app", AppController(self.__context))
        self.__controllers.add("auth", AuthController(self.__context))


if __name__ == "__main__":
    ft.app(target=App().main)
