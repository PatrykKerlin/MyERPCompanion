from typing import Any

from sqlalchemy.orm import relationship as base_relationship
from sqlalchemy.orm.relationships import (
    _RelationshipDeclared,
    _LazyLoadArgumentType,
    _RelationshipArgumentType,
    _ORMColCollectionArgument,
)


def relationship(
    argument: _RelationshipArgumentType[Any],
    back_populates: str,
    foreign_keys: _ORMColCollectionArgument,
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
        lazy=lazy,
        info=info,
        **kwargs,
    )
