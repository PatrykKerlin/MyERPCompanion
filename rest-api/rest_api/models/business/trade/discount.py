from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_category_discount import AssocCategoryDiscount
    from .assoc_customer_discount import AssocCustomerDiscount
    from .assoc_item_discount import AssocItemDiscount
    from .customer import Customer
    from ..logistic.category import Category
    from ..logistic.item import Item


class Discount(BaseModel):
    __tablename__ = "discounts"
    __table_args__ = (
        CheckConstraint(
            "(percent IS NULL AND amount IS NOT NULL) OR (percent IS NOT NULL AND amount IS NULL)",
            name="ck_discount_one_of_percent_or_amount",
        ),
        CheckConstraint("end_date IS NULL OR start_date <= end_date", name="ck_discount_valid_dates"),
    )

    key: Mapped[str] = Fields.key()
    index: Mapped[str] = Fields.string_10(unique=True)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    start_date: Mapped[datetime] = Fields.datetime()
    end_date: Mapped[datetime | None] = Fields.datetime(nullable=True)

    percent: Mapped[float | None] = Fields.numeric_3_2(nullable=True)
    amount: Mapped[float | None] = Fields.numeric_10_2(nullable=True)

    min_order_value: Mapped[float | None] = Fields.numeric_10_2(nullable=True)
    min_quantity: Mapped[int | None] = Fields.integer(nullable=True)

    discount_categories: Mapped[list[AssocCategoryDiscount]] = Fields.relationship(
        argument="AssocCategoryDiscount", back_populates="discount", foreign_keys="AssocCategoryDiscount.discount_id"
    )
    discount_customers: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount", back_populates="discount", foreign_keys="AssocCustomerDiscount.discount_id"
    )
    discount_items: Mapped[list[AssocItemDiscount]] = Fields.relationship(
        argument="AssocItemDiscount", back_populates="discount", foreign_keys="AssocItemDiscount.discount_id"
    )

    @property
    def categories(self) -> list[Category]:
        return [row.category for row in self.discount_categories]

    @property
    def customers(self) -> list[Customer]:
        return [row.customer for row in self.discount_customers]

    @property
    def items(self) -> list[Item]:
        return [row.item for row in self.discount_items]
