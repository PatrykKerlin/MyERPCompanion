from typing import Type, TypeVar, Generic
from schemas.base import BaseCreateSchema, BaseUpdateSchema
from entities.base import BaseEntity
from helpers.helpers import create_or_update_instance

TBaseEntity = TypeVar("TBaseEntity", bound="BaseEntity")
TDTO = TypeVar("TDTO", bound="BaseDTO")
TCreateSchema = TypeVar("TCreateSchema", bound="BaseCreateSchema")
TUpdateSchema = TypeVar("TUpdateSchema", bound="BaseUpdateSchema")


class BaseDTO(Generic[TDTO]):
    def __init__(self, id: int | None) -> None:
        self.id = id

    @classmethod
    def from_entity(cls: Type[TDTO], entity: TBaseEntity) -> TDTO:
        return create_or_update_instance(cls, entity.__dict__)

    @classmethod
    def from_schema(cls: Type[TDTO], schema: TCreateSchema | TUpdateSchema | dict) -> TDTO:
        schema_dict = schema if isinstance(schema, dict) else schema.dict(exclude_unset=True)
        del schema
        return create_or_update_instance(cls, schema_dict)

    @classmethod
    def call_all_deleters(cls, instance: TDTO) -> None:
        for name in dir(instance.__class__):
            attr = getattr(instance.__class__, name)
            if isinstance(attr, property) and attr.fdel is not None:
                try:
                    delattr(instance, name)
                except AttributeError:
                    pass
