from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .language import Language


class Translation(BaseModel):
    __tablename__ = "translations"
    __table_args__ = (UniqueConstraint("key", "language_id", name="uq_translations_key_language"),)

    key: Mapped[str] = mapped_column(String(25), nullable=False)
    value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)
    language: Mapped[Language] = relationship(
        argument="Language", back_populates="translations", foreign_keys=[language_id]
    )
