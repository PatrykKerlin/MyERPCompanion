from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Group(BaseEntity):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship(
        argument="User",
        secondary="users_groups",
        primaryjoin="Group.id == users_groups.c.group_id",
        secondaryjoin="User.id == users_groups.c.user_id",
        back_populates="groups",
    )
    modules: Mapped[list["Module"]] = relationship(
        argument="Module",
        secondary="groups_modules",
        primaryjoin="Group.id == groups_modules.c.group_id",
        secondaryjoin="Module.id == groups_modules.c.user_id",
        back_populates="groups",
    )
