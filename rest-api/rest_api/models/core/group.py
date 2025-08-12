from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .module_group import ModuleGroup
    from .user_group import UserGroup
    from .module import Module
    from .user import User


class Group(BaseModel):
    __tablename__ = "groups"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    group_modules: Mapped[list[ModuleGroup]] = relationship(
        argument="ModuleGroup", back_populates="group", foreign_keys="ModuleGroup.group_id"
    )
    group_users: Mapped[list[UserGroup]] = relationship(
        argument="UserGroup", back_populates="group", foreign_keys="UserGroup.group_id"
    )

    @property
    def modules(self) -> list[Module]:
        return [row.module for row in self.group_modules]

    @property
    def users(self) -> list[User]:
        return [row.user for row in self.group_users]
