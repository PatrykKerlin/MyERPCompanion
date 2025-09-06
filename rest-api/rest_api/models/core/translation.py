from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .language import Language


class Translation(BaseModel):
    __tablename__ = "translations"
    __table_args__ = (UniqueConstraint("key", "language_id", name="uq_translations_key_language"),)

    key: Mapped[str] = Fields.key()
    value: Mapped[str] = Fields.string_1000()

    language_id: Mapped[int] = Fields.foreign_key(column="languages.id")
    language: Mapped[Language] = Fields.relationship(
        argument="Language", back_populates="translations", foreign_keys=[language_id]
    )
