from typing import Generic, Type, TypeVar, Any

from pydantic import BaseModel

from entities.base import BaseEntity
from schemas.base import BaseCreateSchema

TBaseEntity = TypeVar("TBaseEntity", bound=BaseEntity)
TDTO = TypeVar("TDTO", bound="BaseDTO")
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)


class BaseDTO(BaseModel, Generic[TDTO, TBaseEntity, TCreateSchema]):
    id: int | None = None

    model_config = {"from_attributes": True}

    def to_entity(self, entity_cls: type[TBaseEntity]) -> TBaseEntity:
        entity_data = self.model_dump(exclude_unset=True)
        return entity_cls(**entity_data)

    @classmethod
    def from_entity(cls: type[TDTO], entity: TBaseEntity) -> TDTO:
        return cls.model_validate(entity)

    @classmethod
    def from_schema(
        cls: type[TDTO], schema: TCreateSchema | dict[str, Any]
    ) -> TDTO:
        schema_dict = (
            schema
            if isinstance(schema, dict)
            else schema.model_dump(exclude_unset=True)
        )
        return cls.model_validate(schema_dict)
