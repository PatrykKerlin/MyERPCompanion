from typing import Callable

from config import Settings
from config.database import Database
from entities.core import Group, User
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from schemas.core import UserResponse
from services.core import AuthService
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria


class CurrentUserController:
    def __init__(
        self, get_db: Callable, settings: Settings, oauth2_scheme: OAuth2PasswordBearer
    ):
        self.__get_db = get_db
        self.__settings = settings
        self.__oauth2_scheme = oauth2_scheme
        self.router = APIRouter()
        self.router.add_api_route(
            "/current-user",
            self.current_user,
            methods=["GET"],
            response_model=UserResponse,
        )

    async def current_user(self, request: Request) -> dict:
        token = await self.__oauth2_scheme(request)
        payload = AuthService.decode_access_token(token, self.__settings)
        if not payload or "user" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user_id = payload["user"]

        async with self.__get_db() as db:
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.groups),
                    with_loader_criteria(Group, Group.is_active == True),
                )
                .filter(User.id == user_id, User.is_active == True)
            )
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            return user
