from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .group import Group
    from .language import Language
    from .theme import Theme


class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=True)

    language: Mapped["Language"] = relationship(
        back_populates="users", foreign_keys=[language_id], lazy="selectin"
    )
    theme: Mapped["Theme"] = relationship(
        back_populates="users", foreign_keys=[theme_id], lazy="selectin"
    )

    groups: Mapped[list["Group"]] = relationship(
        argument="Group",
        secondary="users_groups",
        primaryjoin="User.id == users_groups.c.user_id",
        secondaryjoin="Group.id == users_groups.c.group_id",
        back_populates="users",
        lazy="selectin",
    )
