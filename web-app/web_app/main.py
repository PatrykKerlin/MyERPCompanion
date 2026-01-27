import logging
import os
from importlib import util
from typing import Callable

import flet as ft


def _load_desktop_main() -> Callable:
    try:
        from desktop_app.main import main as desktop_main  # type: ignore

        return desktop_main
    except Exception:
        spec = util.spec_from_file_location("desktop_app_main", "/desktop_app/main.py")
        if spec is None or spec.loader is None:
            raise RuntimeError("Failed to load desktop_app main module.")
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.main


class App:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

    def run(self) -> None:
        app_main = _load_desktop_main()
        host = os.getenv("FLET_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("FLET_SERVER_PORT", "8550"))
        ft.app(target=app_main, view=ft.AppView.WEB_BROWSER, host=host, port=port)


def main() -> None:
    App().run()


if __name__ == "__main__":
    main()
