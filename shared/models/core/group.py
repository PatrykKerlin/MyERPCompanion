from __future__ import annotations

from typing import TYPE_CHECKING

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

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    group_modules: Mapped[list[AssocModuleGroup]] = Fields.relationship(
        argument="AssocModuleGroup", back_populates="group", foreign_keys="AssocModuleGroup.group_id"
    )
    group_users: Mapped[list[AssocUserGroup]] = Fields.relationship(
        argument="AssocUserGroup", back_populates="group", foreign_keys="AssocUserGroup.group_id"
    )
