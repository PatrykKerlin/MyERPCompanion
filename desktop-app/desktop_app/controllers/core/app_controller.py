import asyncio
from concurrent.futures import Future

import customtkinter as ctk

from config import Context
from controllers.base import BaseController
from services.core import AppService
from views.core import AppWindow
from views.components import LoadingModal


class AppController(BaseController[AppService, AppWindow]):
    _service_cls = AppService
    _view_cls = AppWindow

    def __init__(self, master: ctk.CTk, context: Context) -> None:
        super().__init__(master, context)
        self.__loading_modal = LoadingModal(master, self, self._context.texts)

    def show(self) -> None:
        super().show()
        self.__loading_modal.show()

        future = asyncio.run_coroutine_threadsafe(self.__initialize(), self._context.loop)
        future.add_done_callback(self.__on_initialize_done)

    async def __initialize(self) -> None:
        await self._service.check_redis_ready()
        await self._service.load_settings_from_redis()
        await self._service.api_health_check()
        texts = await self._service.fetch_texts()
        self._context.texts = texts

    def __on_initialize_done(self, future: Future[None]) -> None:
        if not self._master.winfo_exists():
            return

        def update_ui():
            try:
                future.result()
                self._view.rebuild_window()
                self.__loading_modal.destroy()
                self._context.controllers.auth.show()
            except Exception as e:
                print(f"Startup error: {e}")
                self.__loading_modal.destroy()
                ctk.CTkLabel(self._view, text=f"Startup error:\n{e}").pack(pady=20)

        self._master.after(0, update_ui)
