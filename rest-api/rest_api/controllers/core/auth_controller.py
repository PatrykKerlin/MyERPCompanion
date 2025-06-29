from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose.exceptions import JWTError
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from config import Context
from schemas.core import AuthStrictSchema
from utils.auth import Auth


class AuthController:
    def __init__(self, context: Context) -> None:
        self.__settings = context.settings
        self.__get_session = context.get_session
        self.router = APIRouter()
        self.router.add_api_route("/auth", self.auth, methods=["POST"])
        self.router.add_api_route("/refresh", self.refresh, methods=["POST"])

    async def auth(self, data: AuthStrictSchema) -> JSONResponse:
        try:
            async with self.__get_session() as session:
                response = await Auth.authenticate(session, data.username, data.password, self.__settings)
                if not response:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
                return JSONResponse(response)
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def refresh(self, request: Request) -> JSONResponse:
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            refresh_token = auth_header.split(" ")[1]
            async with self.__get_session() as session:
                schema = await Auth.validate_refresh_token(session, refresh_token, self.__settings)
                new_access_token = Auth.create_access_token(schema.id, self.__settings)
                return JSONResponse(content={"access": new_access_token})
        except (JWTError, KeyError, NoResultFound):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
