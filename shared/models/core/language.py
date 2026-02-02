from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.translation import Translation
    from models.core.user import User


class Language(BaseModel):
    __tablename__ = "languages"

    __table_args__ = (Index("ux_language_key_active_true", "key", unique=True, postgresql_where=text("is_active")),)

    key: Mapped[str] = Fields.key(unique=False)
    symbol: Mapped[str] = Fields.symbol()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    translations: Mapped[list[Translation]] = Fields.relationship(
        argument="Translation",
        back_populates="language",
        foreign_keys="Translation.language_id",
        cascade_soft_delete=True,
    )
    users: Mapped[list[User]] = Fields.relationship(
        argument="User", back_populates="language", foreign_keys="User.language_id"
    )
