from types import new_class
from typing import TypeVar

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService

TPlainSchema = TypeVar("TPlainSchema", bound=BasePlainSchema)
TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)


class ServiceFactory:
    @classmethod
    def create(
        cls,
        name_prefix: str,
        plain_schema_cls: type[TPlainSchema],
        strict_schema_cls: type[TStrictSchema],
    ) -> type[BaseService[TPlainSchema, TStrictSchema]]:
        return new_class(
            f"{name_prefix}Service",
            [BaseService[plain_schema_cls, strict_schema_cls]],
            exec_body=lambda namespace: namespace.update({"_plain_schema_cls": plain_schema_cls}),
        )
