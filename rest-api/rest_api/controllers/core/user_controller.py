from typing import Callable, List

from config import Settings
from controllers.base import BaseController
from dtos.core import UserDTO
from entities.core import User
from fastapi import APIRouter, Request, status
from fastapi.security import OAuth2PasswordBearer
from schemas.core import UserCreate, UserResponse
from services.core import UserService


class UserController(BaseController):
	def __init__(
		self, get_db: Callable, settings: Settings, oauth2_scheme: OAuth2PasswordBearer
	) -> None:
		super().__init__(
			get_db=get_db,
			settings=settings,
			oauth2_scheme=oauth2_scheme,
			service=UserService(),
			response_schema=UserResponse,
			create_schema=UserCreate,
			require_auth=True,
			required_groups=[],
			entity_name=User.__name__,
		)
		self.router.add_api_route(
			"", self.get_all, methods=["GET"], response_model=List[UserResponse]
		)
		self.router.add_api_route(
			"/{user_id}", self.get_by_id, methods=["GET"], response_model=UserResponse
		)
		self.router.add_api_route(
			"",
			self.create,
			methods=["POST"],
			response_model=UserResponse,
			status_code=status.HTTP_201_CREATED,
		)
		self.router.add_api_route(
			"/{user_id}", self.update, methods=["PUT"], response_model=UserResponse
		)
		self.router.add_api_route(
			"/{user_id}",
			self.delete,
			methods=["DELETE"],
			status_code=status.HTTP_204_NO_CONTENT,
		)

	async def get_all(self, request: Request):
		return await super().get_all(request)

	async def get_by_id(self, request: Request, user_id: int):
		return await super().get_by_id(request, user_id)

	async def create(self, request: Request, data: UserCreate):
		return await super().create(request, data)

	async def update(self, request: Request, user_id: int, data: UserCreate):
		return await super().update(request, user_id, data)

	async def delete(self, request: Request, user_id: int):
		return await super().delete(request, user_id)
