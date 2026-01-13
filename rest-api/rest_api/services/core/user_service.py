from __future__ import annotations

from typing import TYPE_CHECKING, Union

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import AssocUserGroup, User
from repositories.core import AssocUserGroupRepository, GroupRepository, UserRepository
from schemas.core.user_schema import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema
from services.base.base_service import BaseService

if TYPE_CHECKING:
    from utils.auth import Auth


class UserService(
    BaseService[
        User,
        UserRepository,
        Union[UserStrictCreateSchema, UserStrictUpdateSchema],
        UserPlainSchema,
    ]
):
    _repository_cls = UserRepository
    _model_cls = User
    _output_schema_cls = UserPlainSchema

    def __init__(self) -> None:
        super().__init__()
        self.__auth: Auth | None = None

    def set_auth(self, auth: Auth) -> None:
        self.__auth = auth

    async def get_one_by_username(self, session: AsyncSession, username: str) -> UserPlainSchema | None:
        model = await self._repository_cls.get_one_by_username(session, username)
        if not model:
            return None
        return self._output_schema_cls.model_validate(model)

    async def create(
        self, session: AsyncSession, created_by: int, schema: Union[UserStrictCreateSchema, UserStrictUpdateSchema]
    ) -> UserPlainSchema:
        model = self._model_cls(**schema.model_dump(exclude={"groups"}))
        model.created_by = created_by
        if schema.password:
            model.password = self.__auth.get_password_hash(schema.password) if self.__auth else ""
        saved_model = await self._repository_cls.save(session, model)
        return self._output_schema_cls.model_validate(saved_model)

    async def update(
        self,
        session: AsyncSession,
        model_id: int,
        modified_by: int,
        schema: Union[UserStrictCreateSchema, UserStrictUpdateSchema],
    ) -> UserPlainSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        for key, value in schema.model_dump(exclude_unset=True, exclude={"groups", "password"}).items():
            setattr(model, key, value)
        model.modified_by = modified_by
        if schema.password:
            model.password = self.__auth.get_password_hash(schema.password) if self.__auth else ""
        updated_model = await self._repository_cls.save(session, model)
        return self._output_schema_cls.model_validate(updated_model)
