from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .language import Language


class Text(BaseModel):
    __tablename__ = "texts"
    __table_args__ = (UniqueConstraint("key", "language_id", name="uq_texts_key_language"),)

    key: Mapped[str] = mapped_column(String(25), nullable=False)
    value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)
    language: Mapped[Language] = relationship(argument="Language", back_populates="texts", foreign_keys=[language_id])
