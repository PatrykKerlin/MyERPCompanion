import flet as ft
import logging

from config.context import Context
from config.controllers import Controllers
from config.default_translation import DefaultTranslation
from config.settings import Settings


class App:
    def main(self, page: ft.Page) -> None:
        settings = Settings()  # type: ignore
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        logger = logging.getLogger("app")
        context = Context(
            settings=settings,
            page=page,
            logger=logger,
            texts=DefaultTranslation().texts,
        )
        controllers = Controllers(context)
        context.controllers = controllers
        controllers.initialize_window_controllers()
        app_controller = controllers.get("app")
        app_controller.show()


if __name__ == "__main__":
    ft.app(target=App().main)
