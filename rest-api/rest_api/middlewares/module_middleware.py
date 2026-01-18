from collections.abc import Callable
from typing import Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.context import Context
from services.core.module_service import ModuleService


class ModuleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, context: Context) -> None:
        super().__init__(app)
        self.__get_session = context.get_session
        self.__header = context.settings.MODULE_HEADER
        self.__module_service = ModuleService()

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.module = None

        module_id_str = request.headers.get(self.__header)
        if module_id_str:
            try:
                module_id = int(module_id_str)
                session = getattr(request.state, "db", None)
                if session is None:
                    raise RuntimeError("Database session is not initialized.")
                module_schema = await self.__module_service.get_one_by_id(session, module_id)
                request.state.module = module_schema
            except Exception:
                pass

        return await call_next(request)
