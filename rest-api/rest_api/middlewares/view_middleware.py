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

        view_id_str = request.headers.get(self.__header)
        if view_id_str and view_id_str.isdigit():
            view_id = int(view_id_str)
            async with self.__get_session() as session:
                view_service = ViewService()
                view_schema = await view_service.get_one_by_id(session, view_id)
                request.state.view = view_schema

        return await call_next(request)
