from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.delivery_method import DeliveryMethod
    from models.business.logistic.item import Item


class Unit(BaseModel):
    __tablename__ = "units"

    name: Mapped[str] = Fields.name()
    symbol: Mapped[str] = Fields.symbol()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    items: Mapped[list[Item]] = Fields.relationship(argument="Item", back_populates="unit", foreign_keys="Item.unit_id")
    delivery_methods: Mapped[DeliveryMethod] = Fields.relationship(
        argument="DeliveryMethod", back_populates="unit", foreign_keys="DeliveryMethod.unit_id"
    )
