from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import literal_column, select
from sqlalchemy.orm import Mapped, column_property

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
    from models.business.trade.discount import Discount
    from models.business.trade.order import Order
    from models.core.user import User


class Customer(BaseModel):
    __tablename__ = "customers"

    first_name: Mapped[str] = Fields.string_50(nullable=True)
    last_name: Mapped[str] = Fields.string_50(nullable=True)

    company_name: Mapped[str | None] = Fields.name()

    payment_term: Mapped[int] = Fields.integer()
    tax_id: Mapped[str] = Fields.string_10()

    email: Mapped[str] = Fields.string_100(unique=True)
    phone_number: Mapped[str] = Fields.string_20(unique=True)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    shipping_street: Mapped[str | None] = Fields.string_50(nullable=True)
    shipping_house_number: Mapped[str | None] = Fields.string_10(nullable=True)
    shipping_apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    shipping_postal_code: Mapped[str | None] = Fields.postal_code(nullable=True)
    shipping_city: Mapped[str | None] = Fields.string_50(nullable=True)
    shipping_country: Mapped[str | None] = Fields.string_50(nullable=True)

    user_id: Mapped[int | None] = Fields.foreign_key(column="users.id", unique=True)
    user: Mapped[User | None] = Fields.relationship(
        argument="User", back_populates="customer", foreign_keys=[user_id], uselist=False
    )

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="customer", foreign_keys="Order.customer_id"
    )
    customer_discounts: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount", back_populates="customer", foreign_keys="AssocCustomerDiscount.customer_id"
    )

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.customer_discounts]
