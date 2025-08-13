from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_customer_discount import AssocCustomerDiscount
    from .discount import Discount
    from .order import Order


class Customer(BaseModel):
    __tablename__ = "customers"

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    is_company: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    company_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    payment_term: Mapped[int] = mapped_column(Integer, nullable=False)

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    use_one_address: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    shipping_street: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shipping_house_number: Mapped[str] = mapped_column(String(10), nullable=False)
    shipping_apartment_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    shipping_postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    shipping_city: Mapped[str] = mapped_column(String(50), nullable=False)
    shipping_country: Mapped[str] = mapped_column(String(50), nullable=False)

    billing_street: Mapped[str | None] = mapped_column(String(50), nullable=True)
    billing_house_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    billing_apartment_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    billing_postal_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    billing_city: Mapped[str | None] = mapped_column(String(50), nullable=True)
    billing_country: Mapped[str | None] = mapped_column(String(50), nullable=True)

    orders: Mapped[list[Order]] = relationship(
        argument="Order", back_populates="customer", foreign_keys="Order.customer_id"
    )
    customer_discounts: Mapped[list[AssocCustomerDiscount]] = relationship(
        argument="AssocCustomerDiscount", back_populates="customer", foreign_keys="AssocCustomerDiscount.customer_id"
    )

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.customer_discounts]
