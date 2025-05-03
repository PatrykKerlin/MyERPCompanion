import asyncio
import locale
import threading

import customtkinter as ctk

from config import Context, Controllers, Settings
from controllers.core import AppController, AuthController


class App:
    def __init__(self) -> None:
        self.__master = ctk.CTk()
        self.__init_locale()
        settings = Settings()  # type: ignore
        loop = asyncio.new_event_loop()
        language = self.__detect_language()
        controllers = Controllers()
        self.__context = Context(settings=settings, loop=loop, controllers=controllers, language=language)
        self.__start_async_loop()
        self.__register_controllers()

    def __init_locale(self) -> None:
        ctk.set_appearance_mode("system")
        locale.setlocale(locale.LC_ALL, "")

    def __detect_language(self) -> str:
        current_locale = locale.getlocale()
        return current_locale[0].split("_")[0] if current_locale[0] else "en"

    def __start_async_loop(self) -> None:
        threading.Thread(target=self.__run_loop, daemon=True).start()

    def __run_loop(self) -> None:
        asyncio.set_event_loop(self.__context.loop)
        self.__context.loop.run_forever()

    def __register_controllers(self) -> None:
        self.__context.controllers.add("app", AppController(self.__master, self.__context))
        self.__context.controllers.add("auth", AuthController(self.__master, self.__context))

    def run(self) -> None:
        self.__context.controllers.app.show()
        self.__master.mainloop()


if __name__ == "__main__":
    App().run()
