from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .endpoint import Endpoint
    from .group import Group


class Module(BaseModel):
    __tablename__ = "modules"

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    endpoints: Mapped[list["Endpoint"]] = relationship(
        argument="Endpoint",
        back_populates="module",
        foreign_keys="Endpoint.module_id",
    )
    groups: Mapped[list["Group"]] = relationship(
        argument="Group",
        secondary="groups_modules",
        primaryjoin="Module.id == groups_modules.c.module_id",
        secondaryjoin="Group.id == groups_modules.c.group_id",
        back_populates="modules",
    )
