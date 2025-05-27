from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .group import Group
    from .module import Module


class AssocGroupModule(BaseModel):
    __tablename__ = "groups_modules"

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), primary_key=True)
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("modules.id"), primary_key=True)

    group: Mapped[Group] = relationship(argument="Group", back_populates="group_modules", foreign_keys=[group_id])
    module: Mapped[Module] = relationship(argument="Module", back_populates="module_groups", foreign_keys=[module_id])
