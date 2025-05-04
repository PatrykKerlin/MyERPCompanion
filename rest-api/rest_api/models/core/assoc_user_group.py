from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .group import Group
    from .user import User


class AssocUserGroup(BaseModel):
    __tablename__ = "users_groups"

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)

    group: Mapped[Group] = relationship(argument="Group", back_populates="group_users", foreign_keys=[group_id])
    user: Mapped[User] = relationship(argument="User", back_populates="user_groups", foreign_keys=[user_id])
