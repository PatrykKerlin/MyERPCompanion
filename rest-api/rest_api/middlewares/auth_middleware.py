from collections.abc import Callable
from typing import Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import Context
from services.core import UserService
from utils.auth import Auth


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, context: Context) -> None:
        super().__init__(app)
        self.__settings = context.settings
        self.__get_session = context.get_session

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.user = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split(" ")[1]
            payload = Auth.decode_access_token(token, self.__settings)
            user_id = payload.get("user")

            if isinstance(user_id, int) and payload.get("type") == "access":
                user_service = UserService()
                async with self.__get_session() as session:
                    user_schema = await user_service.get_one_by_id(session, user_id)
                    request.state.user = user_schema

        return await call_next(request)
