from datetime import UTC, datetime
from typing import Awaitable
from collections.abc import Callable

from config import Settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response

from services.core import UserService
from services.core import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        super().__init__(app)
        self.__settings = settings

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        auth_header = request.headers.get("Authorization", None)
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split(" ")[1]
            payload = AuthService.decode_auth_token(token, self.__settings)
            user_id = payload.get("user", None)
            iat = payload.get("iat", None)

            if user_id and iat:
                user = await UserService.get_by_id(user_id)
                if user and datetime.fromtimestamp(iat, UTC) < user.pwd_modified_at:
                    request.state.user = user

        return await call_next(request)
