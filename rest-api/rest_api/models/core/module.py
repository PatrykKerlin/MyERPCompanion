from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_group_module import AssocGroupModule
    from .group import Group
    from .view import View


class Module(BaseModel):
    __tablename__ = "modules"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)

    views: Mapped[list[View]] = relationship(argument="View", back_populates="module", foreign_keys="View.module_id")
    module_groups: Mapped[list[AssocGroupModule]] = relationship(
        argument="AssocGroupModule", back_populates="module", foreign_keys="AssocGroupModule.module_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [assoc.group for assoc in self.module_groups]
