from typing import Any

from sqlalchemy.orm import relationship as base_relationship
from sqlalchemy.orm.relationships import _RelationshipDeclared, _LazyLoadArgumentType


def relationship(
    lazy: _LazyLoadArgumentType = "selectin", cascade_soft_delete: bool = True, **kwargs: Any
) -> _RelationshipDeclared[Any]:
    info = kwargs.pop("info", {}) or {}
    info["cascade_soft_delete"] = cascade_soft_delete
    return base_relationship(lazy=lazy, info=info, **kwargs)
