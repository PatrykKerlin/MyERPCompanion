from collections.abc import Callable
from typing import Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import Context
from services.core import ViewService


class ViewMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, context: Context) -> None:
        super().__init__(app)
        self.__get_session = context.get_session
        self.__header = context.settings.VIEW_HEADER

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.view = None

        view_key = request.headers.get(self.__header)
        if view_key:
            view_service = ViewService()
            async with self.__get_session() as session:
                view_schema = await view_service.get_one_by_key(session, view_key)
                request.state.view = view_schema

        return await call_next(request)
