from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity

if TYPE_CHECKING:
    from .language import Language


class Text(BaseEntity):
    __tablename__ = "texts"

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)

    language: Mapped["Language"] = relationship(
        back_populates="texts", foreign_keys=[language_id], lazy="selectin"
    )
