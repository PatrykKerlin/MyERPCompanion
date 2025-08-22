from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .order import Order
    from .currency import Currency
    from ..logistic.unit import Unit


class DeliveryMethod(BaseModel):
    __tablename__ = "delivery_methods"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    carrier: Mapped[str] = Fields.string_50()
    price_per_unit: Mapped[float] = Fields.numeric_10_2()

    max_width: Mapped[float] = Fields.integer()
    max_height: Mapped[float] = Fields.integer()
    max_length: Mapped[float] = Fields.integer()
    max_weight: Mapped[float] = Fields.integer()

    unit_id: Mapped[int] = Fields.foreign_key(column="units.id")
    unit: Mapped[Unit] = Fields.relationship(argument="Unit", back_populates="delivery_methods", foreign_keys=[unit_id])

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="delivery_methods", foreign_keys=[currency_id]
    )

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="delivery_method", foreign_keys="Order.id"
    )
