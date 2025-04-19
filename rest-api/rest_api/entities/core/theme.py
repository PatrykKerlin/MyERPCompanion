from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .user import User


class Theme(BaseEntity):
    __tablename__ = "themes"

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(
        back_populates="theme", foreign_keys="User.theme_id", lazy="selectin"
    )
