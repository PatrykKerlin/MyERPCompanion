from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.assoc_module_group import AssocModuleGroup
    from models.core.assoc_user_group import AssocUserGroup
    from models.core.module import Module
    from models.core.user import User


class Group(BaseModel):
    __tablename__ = "groups"

    __table_args__ = (Index("ux_group_key_active_true", "key", unique=True, postgresql_where=text("is_active")),)

    key: Mapped[str] = Fields.key(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    group_modules: Mapped[list[AssocModuleGroup]] = Fields.relationship(
        argument="AssocModuleGroup",
        back_populates="group",
        foreign_keys="AssocModuleGroup.group_id",
        cascade_soft_delete=True,
    )
    group_users: Mapped[list[AssocUserGroup]] = Fields.relationship(
        argument="AssocUserGroup",
        back_populates="group",
        foreign_keys="AssocUserGroup.group_id",
        cascade_soft_delete=True,
    )
