from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .text import Text
    from .user import User


class Language(BaseModel):
    __tablename__ = "languages"

    key: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    texts: Mapped[list[Text]] = relationship(
        argument="Text", back_populates="language", foreign_keys="Text.language_id"
    )
    users: Mapped[list[User]] = relationship(
        argument="User", back_populates="language", foreign_keys="User.language_id"
    )
