from __future__ import annotations
from typing import Union, TYPE_CHECKING

from models.core import AssocUserGroup, User
from repositories.core import AssocUserGroupRepository, GroupRepository, UserRepository
from schemas.core import UserPlainSchema, UserStrictCreateSchema, UserStrictUpdateSchema
from services.base import BaseService
from utils.auth import Auth
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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

    async def get_by_name(self, session: AsyncSession, username: str) -> UserPlainSchema | None:
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
            model.password = Auth.get_password_hash(schema.password)
        saved_model = await self._repository_cls.save(session, model, False)
        await self._handle_assoc_table(
            session=session,
            assoc_repo_cls=AssocUserGroupRepository,
            model_cls=AssocUserGroup,
            owner_field="user_id",
            related_field="group_id",
            owner_id=saved_model.id,
            related_ids=schema.groups,
            related_repo_cls=GroupRepository,
            created_by=created_by,
        )
        await session.refresh(saved_model)
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
            model.password = Auth.get_password_hash(schema.password)
        updated_model = await self._repository_cls.save(session, model, False)
        await self._handle_assoc_table(
            session=session,
            assoc_repo_cls=AssocUserGroupRepository,
            model_cls=AssocUserGroup,
            owner_field="user_id",
            related_field="group_id",
            owner_id=updated_model.id,
            related_ids=schema.groups,
            related_repo_cls=GroupRepository,
            created_by=modified_by,
            modified_by=modified_by,
        )
        await session.refresh(updated_model)
        return self._output_schema_cls.model_validate(updated_model)
