from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import BaseEntity


class Language(BaseEntity):
    __tablename__ = "languages"

    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(
        back_populates="language", lazy="selectin"
    )
    texts: Mapped[list["Text"]] = relationship(
        back_populates="language", lazy="selectin"
    )
