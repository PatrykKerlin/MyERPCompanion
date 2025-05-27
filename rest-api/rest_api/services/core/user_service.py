from typing import TypeVar, Union

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import AssocUserGroup, User
from repositories.core import AssocUserGroupRepository, GroupRepository, UserRepository
from schemas.base import BaseInputSchema
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.base import BaseService
from utils.auth import Auth
from utils.exceptions import ConflictException, SaveException

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
        created_by: int,
        schema: Union[UserInputCreateSchema, UserInputUpdateSchema],
    ) -> UserOutputSchema:
        model = self._model_cls(**schema.model_dump(exclude={"groups"}))
        model.created_by = created_by
        if schema.password:
            model.password = Auth.get_password_hash(schema.password)
        try:
            saved_model = await self._repository_cls.save(session, model, False)
            if not saved_model:
                raise SQLAlchemyError()
            await self._handle_assoc_table(
                session=session,
                assoc_repo_cls=AssocUserGroupRepository,
                model_cls=AssocUserGroup,
                owner_field="user_id",
                related_field="group_id",
                owner_id=saved_model.id,
                related_ids=schema.groups or [],
                related_repo_cls=GroupRepository,
                created_by=created_by,
            )
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(saved_model)

    async def update(
        self,
        session: AsyncSession,
        model_id: int,
        modified_by: int,
        schema: Union[UserInputCreateSchema, UserInputUpdateSchema],
    ) -> UserOutputSchema | None:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            return None
        for key, value in schema.model_dump(exclude_unset=True, exclude={"groups", "password"}).items():
            setattr(model, key, value)
        model.modified_by = modified_by
        if schema.password:
            model.password = Auth.get_password_hash(schema.password)
        try:
            updated_model = await self._repository_cls.save(session, model)
            if not updated_model:
                raise SQLAlchemyError()
            if schema.groups:
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
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(updated_model)
