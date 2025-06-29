from typing import Any

from sqlalchemy.orm import relationship as base_relationship
from sqlalchemy.orm.relationships import (
    _LazyLoadArgumentType,
    _ORMColCollectionArgument,
    _RelationshipArgumentType,
    _RelationshipDeclared,
)


def relationship(
    argument: _RelationshipArgumentType[Any],
    back_populates: str,
    foreign_keys: _ORMColCollectionArgument,
    uselist: bool = True,
    lazy: _LazyLoadArgumentType = "selectin",
    cascade_soft_delete: bool = True,
    **kwargs: Any,
) -> _RelationshipDeclared[Any]:
    info = kwargs.pop("info", {}) or {}
    info["cascade_soft_delete"] = cascade_soft_delete
    return base_relationship(
        argument=argument,
        back_populates=back_populates,
        foreign_keys=foreign_keys,
        uselist=uselist,
        lazy=lazy,
        info=info,
        **kwargs,
    )
