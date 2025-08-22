from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .discount import Discount
    from .customer import Customer


class AssocCustomerDiscount(BaseModel):
    __tablename__ = "customer_discounts"

    customer_id: Mapped[int] = Fields.foreign_key(column="customers.id", primary_key=True)
    customer: Mapped[Customer] = Fields.relationship(
        argument="Customer", back_populates="customer_discounts", foreign_keys=[customer_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id", primary_key=True)
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_customers", foreign_keys=[discount_id], cascade_soft_delete=False
    )
