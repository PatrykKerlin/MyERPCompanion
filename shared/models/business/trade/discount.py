from __future__ import annotations

from datetime import date
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
    from models.business.trade.currency import Currency
    from models.business.trade.customer import Customer


class Discount(BaseModel):
    __tablename__ = "discounts"

    name: Mapped[str] = Fields.name()
    code: Mapped[str] = Fields.string_10(unique=True)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    start_date: Mapped[date] = Fields.date()
    end_date: Mapped[date | None] = Fields.date(nullable=True)

    percent: Mapped[float | None] = Fields.numeric_3_2(nullable=True)

    min_value: Mapped[float | None] = Fields.numeric_10_2(nullable=True)
    min_quantity: Mapped[int | None] = Fields.integer(nullable=True)

    for_categories: Mapped[bool] = Fields.boolean(default=False)
    for_customers: Mapped[bool] = Fields.boolean(default=False)
    for_items: Mapped[bool] = Fields.boolean(default=False)

    currency_id: Mapped[int | None] = Fields.foreign_key(column="currencies.id", nullable=True)
    currency: Mapped[Currency | None] = Fields.relationship(
        argument="Currency", back_populates="discounts", foreign_keys=[currency_id], cascade_soft_delete=False
    )

    discount_categories: Mapped[list[AssocCategoryDiscount]] = Fields.relationship(
        argument="AssocCategoryDiscount", back_populates="discount", foreign_keys="AssocCategoryDiscount.discount_id"
    )
    discount_customers: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount", back_populates="discount", foreign_keys="AssocCustomerDiscount.discount_id"
    )
    discount_items: Mapped[list[AssocItemDiscount]] = Fields.relationship(
        argument="AssocItemDiscount", back_populates="discount", foreign_keys="AssocItemDiscount.discount_id"
    )

    category_order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="category_discount",
        foreign_keys="AssocOrderItem.category_discount_id",
        cascade_soft_delete=False,
    )
    customer_order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="customer_discount",
        foreign_keys="AssocOrderItem.customer_discount_id",
        cascade_soft_delete=False,
    )
    item_order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="item_discount",
        foreign_keys="AssocOrderItem.item_discount_id",
        cascade_soft_delete=False,
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
