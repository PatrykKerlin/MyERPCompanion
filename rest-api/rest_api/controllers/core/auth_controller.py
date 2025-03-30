from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from config import Context
from schemas.core import AuthCreate
from services.core import AuthService
from utils.exceptions import InvalidCredentialsException


class AuthController:
    def __init__(self, context: Context) -> None:
        self.__context = context
        self.router = APIRouter()
        self.router.add_api_route("/auth", self.auth, methods=["POST"])
        self.router.add_api_route("/refresh", self.auth, methods=["POST"])

    async def auth(self, auth: AuthCreate) -> JSONResponse:
        async with self.__context.get_db() as db:
            response = await AuthService.authenticate(
                db, auth.username, auth.password, self.__context.settings
            )
            if not response:
                raise InvalidCredentialsException
            return JSONResponse(response)

    async def refresh(self, request: Request) -> JSONResponse:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise InvalidCredentialsException()
        refresh_token = auth_header.split(" ")[1]
        user_dto = await AuthService.validate_refresh_token(refresh_token, self.__context.settings)
        new_access_token = AuthService.create_access_token(user_dto.id, self.__context.settings)
        return JSONResponse(content={"access_token": new_access_token})
