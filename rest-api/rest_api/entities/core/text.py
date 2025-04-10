from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Text(BaseEntity):
    __tablename__ = 'texts'

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey('languages.id'), nullable=False)

    language: Mapped["Language"] = relationship(back_populates="texts", lazy="selectin")
