from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_module_group import AssocModuleGroup
    from .assoc_user_group import AssocUserGroup
    from .module import Module
    from .user import User


class Group(BaseModel):
    __tablename__ = "groups"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    group_modules: Mapped[list[AssocModuleGroup]] = relationship(
        argument="AssocModuleGroup", back_populates="group", foreign_keys="AssocModuleGroup.group_id"
    )
    group_users: Mapped[list[AssocUserGroup]] = relationship(
        argument="AssocUserGroup", back_populates="group", foreign_keys="AssocUserGroup.group_id"
    )

    @property
    def modules(self) -> list[Module]:
        return [assoc.module for assoc in self.group_modules]

    @property
    def users(self) -> list[User]:
        return [assoc.user for assoc in self.group_users]
