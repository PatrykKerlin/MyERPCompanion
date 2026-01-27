from importlib import util

import flet as ft


def _load_desktop_main() -> callable:
    spec = util.spec_from_file_location("desktop_app_main", "/desktop_app/main.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load desktop_app main module.")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


if __name__ == "__main__":
    app_main = _load_desktop_main()
    ft.app(target=app_main, view=ft.AppView.FLET_APP)
