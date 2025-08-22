from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_module_group import AssocModuleGroup
    from .assoc_user_group import AssocUserGroup
    from .module import Module
    from .user import User


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

    @property
    def modules(self) -> list[Module]:
        return [row.module for row in self.group_modules]

    @property
    def users(self) -> list[User]:
        return [row.user for row in self.group_users]
