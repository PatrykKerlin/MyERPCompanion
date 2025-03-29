from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Group(BaseEntity):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="users_groups",
        primaryjoin="Group.id == users_groups.c.group_id",
        secondaryjoin="User.id == users_groups.c.user_id",
        back_populates="groups",
    )
