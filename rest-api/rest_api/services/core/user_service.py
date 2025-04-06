from typing import Any, TypeVar, Union

from sqlalchemy.ext.asyncio import AsyncSession

from entities.core import User
from repositories.core import GroupRepository, UserRepository
from schemas.base import BaseCreateSchema
from schemas.core import UserCreate, UserInternal, UserResponse, UserUpdate
from services.base import BaseService
from utils.exceptions import ItemsNotFoundException

TSchema = TypeVar("TSchema", bound=BaseCreateSchema)
UserCreateOrUpdate = Union[UserCreate, UserUpdate]


class UserService(BaseService[User, UserRepository, UserCreateOrUpdate, UserResponse]):
    _repository_cls = UserRepository
    _entity_cls = User
    _response_schema_cls = UserResponse

    async def get_internal_by_id(
        self, session: AsyncSession, user_id: int
    ) -> UserInternal | None:
        entity = await self._repository_cls.get_by_id(session, user_id)
        if not entity:
            return None
        return UserInternal.model_validate(entity)

    async def get_internal_by_name(
        self, session: AsyncSession, username: str
    ) -> UserInternal | None:
        entity = await self._repository_cls.get_by_username(session, username)
        if not entity:
            return None
        return UserInternal.model_validate(entity)

    async def create(
        self, session: AsyncSession, user_id: int, schema: UserCreateOrUpdate
    ) -> UserResponse:
        schema = await self.__prepare_schema(session, schema, UserCreate)
        return await super().create(session, user_id, schema)

    async def update(
        self,
        session: AsyncSession,
        entity_id: int,
        user_id: int,
        schema: UserCreateOrUpdate,
    ) -> UserResponse | None:
        schema = await self.__prepare_schema(
            session, schema, UserUpdate, exclude_unset=True
        )
        return await super().update(session, entity_id, user_id, schema)

    @classmethod
    async def __prepare_schema(
        cls,
        session: AsyncSession,
        schema: TSchema,
        schema_cls: type[TSchema],
        exclude_unset: bool = False,
    ) -> TSchema:
        from utils import AuthUtil

        data = schema.model_dump(exclude_unset=exclude_unset)
        update_fields: dict[str, Any] = {}

        if "groups" in data:
            group_names = data["groups"]
            group_objs = await GroupRepository.get_all_by_names(session, group_names)
            if len(group_objs) != len(group_names):
                found_names = {g.name for g in group_objs}
                missing = list(set(group_names) - found_names)
                raise ItemsNotFoundException("groups", missing)
            update_fields["groups"] = group_objs

        if "password" in data:
            update_fields["password"] = AuthUtil.get_password_hash(data["password"])

        validated = schema_cls.model_validate(data)

        for field, value in update_fields.items():
            setattr(validated, field, value)

        return validated
