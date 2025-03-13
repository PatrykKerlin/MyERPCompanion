from typing import Callable, List
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from models.core import User
from dtos.core import UserDTO
from schemas.core import UserCreate, UserResponse
from config import Settings
from services.core import UserService, AuthService


class UserController:
    def __init__(self, get_db: Callable, settings: Settings, oauth2_scheme: OAuth2PasswordBearer) -> None:
        self.__get_db = get_db
        self.__settings = settings
        self.__oauth2_scheme = oauth2_scheme
        self.__required_groups = ["admins"]
        self.router = APIRouter()
        self.router.add_api_route("", self.get_users, methods=["GET"], response_model=List[UserResponse])
        self.router.add_api_route("/{user_id}", self.get_user, methods=["GET"], response_model=UserResponse)
        self.router.add_api_route("", self.create_user, methods=["POST"], response_model=UserResponse,
                                  status_code=status.HTTP_201_CREATED)
        self.router.add_api_route("/{user_id}", self.update_user, methods=["PUT"], response_model=UserResponse)
        self.router.add_api_route("/{user_id}", self.delete_user, methods=["DELETE"],
                                  status_code=status.HTTP_204_NO_CONTENT)

    async def get_users(self, request: Request) -> List[UserResponse]:
        await self.__check_permissions(request)
        async with self.__get_db() as db:
            dtos = await UserService.get_users(db)
            schemas = [UserResponse(**dto.__dict__) for dto in dtos]
            return schemas

    async def get_user(self, user_id: int, request: Request) -> UserResponse:
        await self.__check_permissions(request)
        async with self.__get_db() as db:
            dto = await UserService.get_user(db, user_id)
            if not dto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            schema = UserResponse(**dto.__dict__)
            return schema

    async def create_user(self, request: Request, user_create: UserCreate) -> UserResponse:
        current_user_dto = await self.__check_permissions(request)
        async with self.__get_db() as db:
            dto = await UserService.create_user(db, user_create, current_user_dto.id)
            schema = UserResponse(**dto.__dict__)
            return schema

    async def update_user(self, user_id: int, request: Request, user_update: UserCreate) -> UserResponse:
        current_user_dto = await self.__check_permissions(request)
        async with self.__get_db() as db:
            dto = await UserService.update_user(db, user_id, user_update, current_user_dto.id)
            if not dto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            schema = UserResponse(**dto.__dict__)
            return schema

    async def delete_user(self, user_id: int, request: Request):
        current_user_dto = await self.__check_permissions(request)
        async with self.__get_db() as db:
            success = await UserService.delete_user(db, user_id, current_user_dto.id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return None

    async def __check_permissions(self, request: Request) -> UserDTO:
        async with self.__get_db() as db:
            result = await AuthService.check_required_groups(db, self.__settings, self.__oauth2_scheme,
                                                             request, self.__required_groups, )
            return result
