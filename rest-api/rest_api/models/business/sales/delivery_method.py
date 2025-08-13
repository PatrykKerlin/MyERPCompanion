from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .order import Order
    from .currency import Currency
    from ..logistic.unit import Unit


class DeliveryMethod(BaseModel):
    __tablename__ = "delivery_methods"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    carrier: Mapped[str] = mapped_column(String(80), nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    max_width: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_height: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_length: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_weight: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"), nullable=False)
    unit: Mapped[Unit] = relationship(argument="Unit", back_populates="delivery_methods", foreign_keys=[unit_id])

    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    currency: Mapped[Currency] = relationship(
        argument="Currency", back_populates="delivery_methods", foreign_keys=[currency_id]
    )

    orders: Mapped[list[Order]] = relationship(
        argument="Order", back_populates="delivery_method", foreign_keys="Order.id"
    )
