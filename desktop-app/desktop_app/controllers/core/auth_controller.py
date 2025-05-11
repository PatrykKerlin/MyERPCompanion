import asyncio

from controllers.base import BaseController
from services.core import AuthService
from views.components import AuthModal


class AuthController(BaseController[AuthService, AuthModal]):
    _service_cls = AuthService
    _view_cls = AuthModal

    def login(self, username: str, password: str) -> None:
        asyncio.run_coroutine_threadsafe(self.__login_async(username, password), self._context.loop)

    async def __login_async(self, username: str, password: str) -> None:
        try:
            tokens = await self._service.fetch_token(username, password)
            self._context.tokens = tokens
            self._view.on_login_success()
        except Exception as e:
            self._view.on_login_error(str(e))
