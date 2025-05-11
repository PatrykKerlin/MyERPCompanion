import asyncio
import locale
import threading

import customtkinter as ctk

from config import Context, Controllers, Settings
from controllers.core import AppController, AuthController


class App:
    def __init__(self) -> None:
        self.__master = ctk.CTk()
        settings = Settings()  # type: ignore
        self.__loop = asyncio.new_event_loop()
        controllers = Controllers()
        self.__context = Context(settings=settings, loop=self.__loop, controllers=controllers)
        self.__start_async_loop()
        self.__register_controllers()
        self.__bind_exit()

        # ctk.set_widget_scaling(1.25)
        # ctk.set_window_scaling(1.25)
        ctk.set_appearance_mode(settings.THEME)

    def __start_async_loop(self) -> None:
        threading.Thread(target=self.__run_loop, daemon=True).start()

    def __run_loop(self) -> None:
        asyncio.set_event_loop(self.__context.loop)
        self.__context.loop.run_forever()

    def __register_controllers(self) -> None:
        self.__context.controllers.add("app", AppController(self.__master, self.__context))
        self.__context.controllers.add("auth", AuthController(self.__master, self.__context))

    def __bind_exit(self) -> None:
        self.__master.protocol("WM_DELETE_WINDOW", self.__shutdown)

    def __shutdown(self) -> None:
        if self.__loop.is_running():
            self.__loop.call_soon_threadsafe(self.__loop.stop)
        self.__master.destroy()

    def run(self) -> None:
        self.__context.controllers.app.show()
        self.__master.mainloop()


if __name__ == "__main__":
    App().run()
