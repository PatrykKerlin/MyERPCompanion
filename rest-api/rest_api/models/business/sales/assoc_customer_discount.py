from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .discount import Discount
    from .customer import Customer


class AssocCustomerDiscount(BaseModel):
    __tablename__ = "customer_discounts"

    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), primary_key=True)
    customer: Mapped[Customer] = relationship(
        argument="Customer", back_populates="customer_discounts", foreign_keys=[customer_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = mapped_column(Integer, ForeignKey("discounts.id"), primary_key=True)
    discount: Mapped[Discount] = relationship(
        argument="Discount", back_populates="discount_customers", foreign_keys=[discount_id], cascade_soft_delete=False
    )
