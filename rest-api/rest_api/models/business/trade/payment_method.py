from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .invoice import Invoice


class PaymentMethod(BaseModel):
    __tablename__ = "payment_methods"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    provider: Mapped[str] = Fields.string_50()
    api_url: Mapped[str] = Fields.string_100()
    surcharge_percent: Mapped[float] = Fields.numeric_3_2()

    invoices: Mapped[list[Invoice]] = Fields.relationship(
        argument="Invoice", back_populates="payment_method", foreign_keys="Invoice.payment_method_id"
    )
