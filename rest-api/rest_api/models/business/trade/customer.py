from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_customer_discount import AssocCustomerDiscount
    from .discount import Discount
    from .order import Order


class Customer(BaseModel):
    __tablename__ = "customers"

    first_name: Mapped[str] = Fields.string_50()
    middle_name: Mapped[str | None] = Fields.string_50(nullable=True)
    last_name: Mapped[str] = Fields.string_50()

    is_company: Mapped[bool] = Fields.boolean(default=False)
    company_name: Mapped[str | None] = Fields.string_100(nullable=True)

    payment_term: Mapped[int] = Fields.integer()

    email: Mapped[str] = Fields.string_100(unique=True)
    phone_number: Mapped[str] = Fields.string_20(unique=True)

    use_one_address: Mapped[bool] = Fields.boolean(default=True)

    shipping_street: Mapped[str | None] = Fields.string_50(nullable=True)
    shipping_house_number: Mapped[str] = Fields.string_10()
    shipping_apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    shipping_postal_code: Mapped[str] = Fields.postal_code()
    shipping_city: Mapped[str] = Fields.string_50()
    shipping_country: Mapped[str] = Fields.string_50()

    billing_street: Mapped[str | None] = Fields.string_50(nullable=True)
    billing_house_number: Mapped[str | None] = Fields.string_10(nullable=True)
    billing_apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    billing_postal_code: Mapped[str | None] = Fields.postal_code(nullable=True)
    billing_city: Mapped[str | None] = Fields.string_50(nullable=True)
    billing_country: Mapped[str | None] = Fields.string_50(nullable=True)

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="customer", foreign_keys="Order.customer_id"
    )
    customer_discounts: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount", back_populates="customer", foreign_keys="AssocCustomerDiscount.customer_id"
    )

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.customer_discounts]
