from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.customer import Customer
    from models.business.trade.discount import Discount


class AssocCustomerDiscount(BaseModel):
    __tablename__ = "customer_discounts"
    __table_args__ = (
        Index(
            "uq_customer_discounts_customer_discount_active_true",
            "customer_id",
            "discount_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    customer_id: Mapped[int] = Fields.foreign_key(column="customers.id")
    customer: Mapped[Customer] = Fields.relationship(
        argument="Customer", back_populates="customer_discounts", foreign_keys=[customer_id], cascade_soft_delete=False
    )

    discount_id: Mapped[int] = Fields.foreign_key(column="discounts.id")
    discount: Mapped[Discount] = Fields.relationship(
        argument="Discount", back_populates="discount_customers", foreign_keys=[discount_id], cascade_soft_delete=False
    )
