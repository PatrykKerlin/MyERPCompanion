from typing import Callable

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria

from config import Context, Settings
from config.database import Database
from entities.core import Group, User
from schemas.core import UserResponse
from services.core import AuthService
from utils.exceptions import InvalidCredentialsException


class CurrentUserController:
    def __init__(self, context: Context) -> None:
        self.__context = context
        self.router = APIRouter()
        self.router.add_api_route(
            "/current-user",
            self.current_user,
            methods=["GET"],
            response_model=UserResponse,
        )

    async def current_user(self, request: Request) -> User:
        token = await self.__context.oauth2_scheme(request)
        if not token:
            raise InvalidCredentialsException()
        payload = AuthService.decode_access_token(token, self.__context.settings)
        if not payload or "user" not in payload:
            raise InvalidCredentialsException()
        user_id = payload["user"]

        async with self.__context.get_db() as db:
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
