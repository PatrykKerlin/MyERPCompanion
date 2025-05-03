from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .setting import Setting


class Text(BaseModel):
    __tablename__ = "texts"
    __table_args__ = (UniqueConstraint("name", "language_id", name="uq_texts_name_language"),)

    name: Mapped[str] = mapped_column(String(25), nullable=False)
    value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("settings.id"), nullable=False)

    language: Mapped["Setting"] = relationship(
        argument="Setting",
        back_populates="text_languages",
        foreign_keys=[language_id],
    )
