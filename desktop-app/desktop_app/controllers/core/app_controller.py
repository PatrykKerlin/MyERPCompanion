from views.core import AppView
from config import Context
from controllers.base import BaseController
from services.core import AppService
import asyncio


class AppController(BaseController[AppService]):
    _service_cls = AppService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._view = AppView(context.page, context.texts, context.settings.THEME)

    def show(self) -> None:
        self._executor.run_async_with_ui_callback(
            async_func=self.__run_startup_sequence,
            sync_func=self._context.controllers.auth.show,
            sync_kwargs={"callback": self.after_login},
        )

    def after_login(self) -> None:
        async def delayed_execution() -> None:
            await asyncio.sleep(0.1)
            self._executor.run_ui(self._view.rebuild, sync_args=[self._context.texts])

        self._executor.run_async(delayed_execution)

    async def __run_startup_sequence(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            await self._service.check_redis_ready()
            await self._service.load_settings_from_redis()
            await self._service.api_health_check()
            texts = await self._service.fetch_texts()
            self._context.texts.update(texts)
            self._close_dialog(loading_dialog)
        except TimeoutError:
            self._close_dialog(loading_dialog)
            self._show_error_dialog("api_not_responding")
