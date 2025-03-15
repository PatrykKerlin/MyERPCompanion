from datetime import UTC, datetime, timedelta
from typing import List

from config import Settings
from dtos.core import UserDTO
from entities.core import Group, User
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from repositories.core import UserRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria


class AuthService:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    @classmethod
    async def authenticate(
        cls, db: AsyncSession, username: str, password: str, settings: Settings
    ) -> str | None:
        user = await UserRepository.get_by_name(db, username)
        if not user or not cls.__verify_password(password, user.password):
            return None
        token_data = {"user": user.id}
        token = cls.__create_access_token(token_data, settings)
        return token

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def decode_access_token(cls, token: str, settings: Settings) -> dict:
        try:
            return jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.JWTError:
            return {}

    @classmethod
    async def get_user_if_authorized(
        cls,
        db: AsyncSession,
        settings: Settings,
        oauth2_scheme: OAuth2PasswordBearer,
        request: Request,
        required_groups: List[str],
    ) -> UserDTO:
        token = await oauth2_scheme(request)
        payload = cls.decode_access_token(token, settings)
        if not payload or "user" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user_id = payload["user"]
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        if not (
            user.is_superuser
            or any(group.name in required_groups for group in user.groups)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        dto = UserDTO.from_entity(user)
        return dto

    @classmethod
    def __verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def __create_access_token(cls, token_data: dict, settings: Settings) -> str:
        expiration_time = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        token_data.update({"exp": expiration_time})
        encoded_jwt = jwt.encode(
            token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
