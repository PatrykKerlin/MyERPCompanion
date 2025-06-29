from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .translation import Translation
    from .user import User


class Language(BaseModel):
    __tablename__ = "languages"

    key: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)

    translations: Mapped[list[Translation]] = relationship(
        argument="Translation", back_populates="language", foreign_keys="Translation.language_id"
    )
    users: Mapped[list[User]] = relationship(
        argument="User", back_populates="language", foreign_keys="User.language_id"
    )
