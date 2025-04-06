from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from config import Context
from schemas.core import AuthCreate
from utils import AuthUtil
from utils.exceptions import InvalidCredentialsException


class AuthController:
    def __init__(self, context: Context) -> None:
        self.__settings = context.settings
        self.__get_session = context.get_session
        self.router = APIRouter()
        self.router.add_api_route("/auth", self.auth, methods=["POST"])
        self.router.add_api_route("/refresh", self.refresh, methods=["POST"])

    async def auth(self, data: AuthCreate) -> JSONResponse:
        async with self.__get_session() as session:
            response = await AuthUtil.authenticate(
                session, data.username, data.password, self.__settings
            )
            if not response:
                raise InvalidCredentialsException()
            return JSONResponse(response)

    async def refresh(self, request: Request) -> JSONResponse:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise InvalidCredentialsException()
        refresh_token = auth_header.split(" ")[1]
        async with self.__get_session() as session:
            schema = await AuthUtil.validate_refresh_token(
                session, refresh_token, self.__settings
            )
            new_access_token = AuthUtil.create_access_token(schema.id, self.__settings)
            return JSONResponse(content={"access_token": new_access_token})
