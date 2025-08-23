from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .translation import Translation
    from .user import User


class Language(BaseModel):
    __tablename__ = "languages"

    key: Mapped[str] = Fields.key()
    symbol: Mapped[str] = Fields.symbol()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    translations: Mapped[list[Translation]] = Fields.relationship(
        argument="Translation", back_populates="language", foreign_keys="Translation.language_id"
    )
    users: Mapped[list[User]] = Fields.relationship(
        argument="User", back_populates="language", foreign_keys="User.language_id"
    )
