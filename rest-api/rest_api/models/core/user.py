from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship
from models.business import Employee

if TYPE_CHECKING:
    from .assoc_user_group import AssocUserGroup
    from .group import Group
    from .language import Language
    from .theme import Theme


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), unique=True, nullable=True)
    employee: Mapped[Employee | None] = relationship(
        argument="Employee", back_populates="user", foreign_keys=[employee_id]
    )

    language_id: Mapped[int | None] = mapped_column(ForeignKey("languages.id"), nullable=True)
    language: Mapped[Language | None] = relationship(
        argument="Language", back_populates="users", foreign_keys=[language_id]
    )

    theme_id: Mapped[int | None] = mapped_column(ForeignKey("themes.id"), nullable=True)
    theme: Mapped[Theme | None] = relationship(argument="Theme", back_populates="users", foreign_keys=[theme_id])

    user_groups: Mapped[list[AssocUserGroup]] = relationship(
        argument="AssocUserGroup", back_populates="user", foreign_keys="AssocUserGroup.user_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [assoc.group for assoc in self.user_groups]
