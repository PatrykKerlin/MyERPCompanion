from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, Numeric, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

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

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    index: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    percent: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    min_order_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    min_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    discount_categories: Mapped[list[AssocCategoryDiscount]] = relationship(
        argument="AssocCategoryDiscount", back_populates="discount", foreign_keys="AssocCategoryDiscount.discount_id"
    )
    discount_customers: Mapped[list[AssocCustomerDiscount]] = relationship(
        argument="AssocCustomerDiscount", back_populates="discount", foreign_keys="AssocCustomerDiscount.discount_id"
    )
    discount_items: Mapped[list[AssocItemDiscount]] = relationship(
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
