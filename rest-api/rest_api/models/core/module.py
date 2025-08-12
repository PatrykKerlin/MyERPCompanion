from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .module_group import ModuleGroup
    from .group import Group
    from .view import View


class Module(BaseModel):
    __tablename__ = "modules"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)

    views: Mapped[list[View]] = relationship(argument="View", back_populates="module", foreign_keys="View.module_id")
    module_groups: Mapped[list[ModuleGroup]] = relationship(
        argument="ModuleGroup", back_populates="module", foreign_keys="ModuleGroup.module_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [row.group for row in self.module_groups]
