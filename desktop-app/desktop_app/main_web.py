import os
from pathlib import Path

import flet as ft
from main import App


def run() -> None:
    os.environ.setdefault("FLET_FORCE_WEB_SERVER", "1")
    host = os.getenv("FLET_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("FLET_SERVER_PORT", "8550"))
    view = getattr(ft.AppView, "WEB_SERVER", ft.AppView.WEB_BROWSER)
    assets_dir = Path(__file__).resolve().parent / "assets"
    upload_dir = Path(os.getenv("FLET_UPLOAD_DIR", str(Path(__file__).resolve().parent / "uploads")))
    os.environ["FLET_UPLOAD_DIR"] = str(upload_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app = App()
    ft.run(
        app.run,
        view=view,
        host=host,
        port=port,
        assets_dir=str(assets_dir),
        upload_dir=str(upload_dir),
    )


if __name__ == "__main__":
    run()
