import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose.exceptions import JWTError
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from schemas.core.auth_schema import AuthStrictSchema
from utils.auth import Auth


class AuthController:
    def __init__(self, auth: Auth) -> None:
        self.__auth = auth
        self.__logger = logging.getLogger("api")
        self.router = APIRouter()
        self.router.add_api_route("/token", self.auth, methods=["POST"])
        self.router.add_api_route("/refresh", self.refresh, methods=["GET"])

    async def auth(self, request: Request, data: AuthStrictSchema) -> JSONResponse:
        try:
            session = getattr(request.state, "db", None)
            if session is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response, error = await self.__auth.authenticate(session, data.username, data.password, data.client)
            if not response:
                if error == "user_not_allowed":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="user_not_allowed"
                    )
                if error == "invalid_client":
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid_client"
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
                )
            return JSONResponse(response)
        except SQLAlchemyError as err:
            self.__logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.auth.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def refresh(self, request: Request) -> JSONResponse:
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            refresh_token = auth_header.split(" ")[1]
            session = getattr(request.state, "db", None)
            if session is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            client = request.headers.get("X-Client")
            schema, token_client = await self.__auth.validate_refresh_token(session, refresh_token, client)
            new_access_token = self.__auth.create_access_token(
                schema.id,
                client=token_client,
            )
            return JSONResponse(content={"access": new_access_token})
        except (JWTError, KeyError, NoResultFound):
            self.__logger.exception(f"AuthError in {self.__class__.__name__}.{self.refresh.__qualname__}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except SQLAlchemyError as err:
            self.__logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.refresh.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
