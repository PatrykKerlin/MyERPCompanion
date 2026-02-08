from collections.abc import Callable
from typing import Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.core import UserService
from utils.auth import Auth


class UserMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, auth: Auth
    ) -> None:
        super().__init__(app)
        self.__auth = auth

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.user = None
        request.state.token_client = None
        request.state.token_warehouse_id = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split(" ")[1]
            payload = self.__auth.decode_access_token(token)
            user_id = payload.get("user")
            token_client = payload.get("client")
            token_warehouse_id = payload.get("warehouse_id")
            request_client = request.headers.get("X-Client")

            if token_client is not None and token_client != request_client:
                return await call_next(request)

            if isinstance(user_id, int) and payload.get("type") == "access":
                user_service = UserService()
                user_service.set_auth(self.__auth)
                session = getattr(request.state, "db", None)
                if session is None:
                    raise RuntimeError("Database session is not initialized.")
                user_schema = await user_service.get_one_by_id(session, user_id)
                request.state.user = user_schema
                request.state.token_client = token_client if isinstance(token_client, str) else None
                request.state.token_warehouse_id = token_warehouse_id if isinstance(token_warehouse_id, int) else None

        return await call_next(request)
