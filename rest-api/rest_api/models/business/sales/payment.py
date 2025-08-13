from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .order import Order


class Payment(BaseModel):
    __tablename__ = "payments"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    api_url: Mapped[str] = mapped_column(String(255), nullable=False)
    surcharge_percent: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)

    orders: Mapped[list[Order]] = relationship(
        argument="Order", back_populates="payment", foreign_keys="Order.payment_id"
    )
