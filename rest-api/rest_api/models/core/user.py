from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_user_group import AssocUserGroup
    from .group import Group
    from .setting import Setting


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    language_id: Mapped[int | None] = mapped_column(ForeignKey("settings.id"), nullable=True)
    theme_id: Mapped[int | None] = mapped_column(ForeignKey("settings.id"), nullable=True)

    language: Mapped[Setting] = relationship(
        argument="Setting", back_populates="user_languages", foreign_keys=[language_id]
    )
    theme: Mapped[Setting] = relationship(argument="Setting", back_populates="user_themes", foreign_keys=[theme_id])
    user_groups: Mapped[list[AssocUserGroup]] = relationship(
        argument="AssocUserGroup", back_populates="user", foreign_keys="AssocUserGroup.user_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [assoc.group for assoc in self.user_groups]
