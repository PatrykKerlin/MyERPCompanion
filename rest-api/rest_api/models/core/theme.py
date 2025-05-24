from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .user import User


class Theme(BaseModel):
    __tablename__ = "themes"

    key: Mapped[str] = mapped_column(String(6), nullable=False, unique=True)
    colors: Mapped[str] = mapped_column(String(25), nullable=True)

    users: Mapped[list[User]] = relationship(argument="User", back_populates="theme", foreign_keys="User.theme_id")
