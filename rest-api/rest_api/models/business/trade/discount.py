from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.category import Category
    from models.business.logistic.item import Item
    from models.business.trade.assoc_category_discount import AssocCategoryDiscount
    from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
    from models.business.trade.assoc_item_discount import AssocItemDiscount
    from models.business.trade.assoc_order_item import AssocOrderItem
    from models.business.trade.customer import Customer


class Discount(BaseModel):
    __tablename__ = "discounts"

    name: Mapped[str] = Fields.name()
    index: Mapped[str] = Fields.string_10(unique=True)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    start_date: Mapped[datetime] = Fields.datetime()
    end_date: Mapped[datetime | None] = Fields.datetime(nullable=True)

    percent: Mapped[float | None] = Fields.numeric_3_2(nullable=True)
    amount: Mapped[float | None] = Fields.numeric_10_2(nullable=True)

    min_value: Mapped[float | None] = Fields.numeric_10_2(nullable=True)
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

    order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem", back_populates="discount", foreign_keys="AssocOrderItem.discount_id"
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
