from typing import Any, TypeVar, Union, cast

from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Group, User
from repositories.core import GroupRepository, UserRepository
from schemas.base import BaseInputSchema
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.base import BaseService
from utils.exceptions import ItemNotFoundException

TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)


class UserService(
    BaseService[
        User,
        UserRepository,
        Union[UserInputCreateSchema, UserInputUpdateSchema],
        UserOutputSchema,
    ]
):
    _repository_cls = UserRepository
    _model_cls = User
    _output_schema_cls = UserOutputSchema

    async def get_by_name(self, session: AsyncSession, username: str) -> UserOutputSchema | None:
        model = await self._repository_cls.get_one_by_username(session, username)
        if not model:
            return None
        return self._output_schema_cls.model_validate(model)

    async def create(
        self,
        session: AsyncSession,
        user_id: int,
        schema: Union[UserInputCreateSchema, UserInputUpdateSchema],
    ) -> UserOutputSchema:
        schema = await self.__prepare_schema(session, schema, UserInputCreateSchema)
        return await super().create(session, user_id, schema)

    async def update(
        self,
        session: AsyncSession,
        model_id: int,
        user_id: int,
        schema: Union[UserInputCreateSchema, UserInputUpdateSchema],
    ) -> UserOutputSchema | None:
        schema = await self.__prepare_schema(session, schema, UserInputUpdateSchema, exclude_unset=True)
        return await super().update(session, model_id, user_id, schema)

    @classmethod
    async def __prepare_schema(
        cls,
        session: AsyncSession,
        schema: TInputSchema,
        schema_cls: type[TInputSchema],
        exclude_unset: bool = False,
    ) -> TInputSchema:
        from utils.auth import Auth

        data = schema.model_dump(exclude_unset=exclude_unset)
        update_fields: dict[str, Any] = {}

        if "groups" in data:
            group_ids = data["groups"]
            groups: list[Group] = []
            for group_id in group_ids:
                group = await GroupRepository.get_one_by_id(session, group_id)
                if not group:
                    ItemNotFoundException(Group.__name__, group_id)
                groups.append(cast(Group, group))
            update_fields["groups"] = groups

        if "password" in data:
            update_fields["password"] = Auth.get_password_hash(data["password"])

        validated = schema_cls.model_validate(data)

        for field, value in update_fields.items():
            setattr(validated, field, value)

        return validated
