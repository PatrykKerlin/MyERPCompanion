from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import Awaitable

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class DbSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, get_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(app)
        self.__get_session = get_session

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        async with self.__get_session() as session:
            request.state.db = session
            try:
                response = await call_next(request)
            except Exception:
                await session.rollback()
                raise
            finally:
                request.state.db = None
            return response
