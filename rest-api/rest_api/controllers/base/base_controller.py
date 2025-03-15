from typing import Callable, List, Type

from config import Settings
from dtos.base import BaseDTO
from dtos.core import UserDTO
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from schemas.base import BaseCreateSchema, BaseResponseSchema
from services.base import BaseService
from services.core import AuthService


class BaseController:
	def __init__(
		self,
		get_db: Callable,
		settings: Settings,
		oauth2_scheme: OAuth2PasswordBearer,
		service: BaseService,
		response_schema: Type[BaseResponseSchema],
		create_schema: Type[BaseCreateSchema],
		require_auth: bool,
		required_groups: list[str],
		entity_name: str,
	) -> None:
		self.router = APIRouter()
		self._get_db = get_db
		self._service = service
		self._response_schema = response_schema
		self._create_schema = create_schema
		self._require_auth = require_auth
		self._entity_name = entity_name
		self.__settings = settings
		self.__oauth2_scheme = oauth2_scheme
		self.__required_groups = required_groups

	async def _get_user_if_authorized(self, request: Request) -> UserDTO | None:
		async with self._get_db() as db:
			dto = await AuthService.get_user_if_authorized(
				db,
				self.__settings,
				self.__oauth2_scheme,
				request,
				self.__required_groups,
			)
			return dto

	async def get_all(self, request: Request) -> List[BaseResponseSchema]:
		if self._require_auth:
			await self._get_user_if_authorized(request)
		async with self._get_db() as db:
			dtos = await self._service.get_all(db)
			return [self._response_schema(**dto.__dict__) for dto in dtos]

	async def get_by_id(self, request: Request, entity_id: int) -> BaseResponseSchema:
		if self._require_auth:
			await self._get_user_if_authorized(request)
		async with self._get_db() as db:
			dto = await self._service.get_by_id(db, entity_id)
			if not dto:
				self.__raise_not_found()
			return self._response_schema(**dto.__dict__)

	async def create(
		self, request: Request, data: BaseCreateSchema
	) -> BaseResponseSchema:
		user_dto = await self._get_user_if_authorized(request)
		async with self._get_db() as db:
			dto = await self._service.create(db, data, user_dto.id)
			return self._response_schema(**dto.__dict__)

	async def update(
		self, request: Request, entity_id: int, data: BaseCreateSchema
	) -> BaseResponseSchema:
		user_dto = await self._get_user_if_authorized(request)
		async with self._get_db() as db:
			dto = await self._service.update(db, entity_id, data, user_dto.id)
			if not dto:
				self.__raise_not_found()
			return self._response_schema(**dto.__dict__)

	async def delete(self, request: Request, entity_id: int) -> None:
		user_dto = await self._get_user_if_authorized(request)
		async with self._get_db() as db:
			success = await self._service.delete(db, entity_id, user_dto.id)
			if not success:
				self.__raise_not_found()
			return None

	def __raise_not_found(self):
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"{self.__entity_name} not found",
		)
