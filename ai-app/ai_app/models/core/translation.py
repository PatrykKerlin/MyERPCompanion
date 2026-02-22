from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.core.language import Language


class Translation(BaseModel):
    __tablename__ = "translations"
    __table_args__ = (
        Index(
            "uq_translations_key_language_active_true",
            "key",
            "language_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    key: Mapped[str] = Fields.key(unique=False)
    value: Mapped[str] = Fields.string_1000()

    language_id: Mapped[int] = Fields.foreign_key(column="languages.id")
    language: Mapped[Language] = Fields.relationship(
        argument="Language", back_populates="translations", foreign_keys=[language_id]
    )
