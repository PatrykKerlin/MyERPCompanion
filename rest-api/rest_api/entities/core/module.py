from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Module(BaseEntity):
    __tablename__ = "modules"

    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    controller: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String(25), nullable=False)
    tag: Mapped[str] = mapped_column(String(25))

    groups: Mapped[list["Group"]] = relationship(
        argument="Group",
        secondary="groups_modules",
        primaryjoin="Module.id == groups_modules.c.module_id",
        secondaryjoin="Group.id == groups_modules.c.group_id",
        back_populates="modules",
    )
