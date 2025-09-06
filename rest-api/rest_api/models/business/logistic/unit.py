from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .item import Item


class Unit(BaseModel):
    __tablename__ = "units"

    key: Mapped[str] = Fields.key()
    symbol: Mapped[str] = Fields.symbol()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    items: Mapped[list[Item]] = Fields.relationship(argument="Item", back_populates="unit", foreign_keys="Item.unit_id")
