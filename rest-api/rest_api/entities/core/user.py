from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .group import Group
    from .setting import Setting


class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    language_id: Mapped[int | None] = mapped_column(ForeignKey("settings.id"), nullable=True)
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("settings.id"), nullable=True)

    language: Mapped["Setting"] = relationship(
        argument="Setting",
        back_populates="user_languages",
        foreign_keys=[language_id],
        lazy="selectin",
    )
    theme: Mapped["Setting"] = relationship(
        argument="Setting",
        back_populates="user_themes",
        foreign_keys=[theme_id],
        lazy="selectin",
    )
    groups: Mapped[list["Group"]] = relationship(
        argument="Group",
        secondary="users_groups",
        primaryjoin="User.id == users_groups.c.user_id",
        secondaryjoin="Group.id == users_groups.c.group_id",
        back_populates="users",
        lazy="selectin",
    )
