from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_group_module import AssocGroupModule
    from .endpoint import Endpoint
    from .group import Group


class Module(BaseModel):
    __tablename__ = "modules"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    endpoints: Mapped[list[Endpoint]] = relationship(
        argument="Endpoint", back_populates="module", foreign_keys="Endpoint.module_id"
    )
    module_groups: Mapped[list[AssocGroupModule]] = relationship(
        argument="AssocGroupModule", back_populates="module", foreign_keys="AssocGroupModule.module_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [assoc.group for assoc in self.module_groups]
