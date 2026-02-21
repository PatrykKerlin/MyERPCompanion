from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from models.core import User
from sqlalchemy import Index, literal_column, select, text
from sqlalchemy.orm import Mapped, column_property

if TYPE_CHECKING:
    from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
    from models.business.trade.invoice import Invoice
    from models.business.trade.order import Order


class Customer(BaseModel):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ux_customer_company_name_active_true", "company_name", unique=True, postgresql_where=text("is_active")),
        Index("ux_customer_email_active_true", "email", unique=True, postgresql_where=text("is_active")),
        Index("ux_customer_phone_number_active_true", "phone_number", unique=True, postgresql_where=text("is_active")),
    )

    first_name: Mapped[str] = Fields.string_50(nullable=True)
    last_name: Mapped[str] = Fields.string_50(nullable=True)

    company_name: Mapped[str] = Fields.name(unique=False)

    payment_term: Mapped[int] = Fields.integer()
    tax_id: Mapped[str] = Fields.string_10()

    email: Mapped[str] = Fields.string_100(unique=False)
    phone_number: Mapped[str] = Fields.string_20(unique=False)

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

    user_id: Mapped[int | None] = column_property(
        select(User.id)
        .where(User.customer_id == literal_column("customers.id"))
        .where(User.is_active.is_(True))
        .scalar_subquery()
    )
    user: Mapped[User | None] = Fields.relationship(
        argument="User", back_populates="customer", foreign_keys="User.customer_id", uselist=False
    )

    invoices: Mapped[list[Invoice]] = Fields.relationship(
        argument="Invoice", back_populates="customer", foreign_keys="Invoice.customer_id"
    )
    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="customer", foreign_keys="Order.customer_id"
    )
    customer_discounts: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount",
        back_populates="customer",
        foreign_keys="AssocCustomerDiscount.customer_id",
        cascade_soft_delete=True,
    )

    @property
    def discount_ids(self) -> list[int]:
        return [row.discount_id for row in self.customer_discounts]
