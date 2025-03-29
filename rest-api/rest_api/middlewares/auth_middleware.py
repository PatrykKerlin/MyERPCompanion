from datetime import UTC, datetime
from typing import Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

from services.core import UserService
from services.core import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Awaitable[Response]):
        auth_header = request.headers.get("Authorization", None)
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split(" ")[1]
            payload = AuthService.decode_auth_token(token)
            user_id = payload.get("user", None)
            iat = payload.get("iat", None)

            if user_id and iat:
                user = await UserService.get_by_id(user_id)
                if user and datetime.fromtimestamp(iat, UTC) < user.pwd_modified_at:
                    request.state.user = user

        return await call_next(request)
