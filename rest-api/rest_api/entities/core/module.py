from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Module(BaseEntity):
    __tablename__ = "modules"

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    endpoints: Mapped[list["Endpoint"]] = relationship(
        back_populates="module",
    )
    groups: Mapped[list["Group"]] = relationship(
        argument="Group",
        secondary="groups_modules",
        primaryjoin="Module.id == groups_modules.c.module_id",
        secondaryjoin="Group.id == groups_modules.c.group_id",
        back_populates="modules",
    )
