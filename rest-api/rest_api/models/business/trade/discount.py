from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.business.trade.assoc_category_discount import AssocCategoryDiscount
    from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
    from models.business.trade.assoc_item_discount import AssocItemDiscount
    from models.business.trade.assoc_order_item import AssocOrderItem
    from models.business.trade.currency import Currency


class Discount(BaseModel):
    __tablename__ = "discounts"
    __table_args__ = (
        Index("ux_discount_name_active_true", "name", unique=True, postgresql_where=text("is_active")),
        Index("ux_discount_code_active_true", "code", unique=True, postgresql_where=text("is_active")),
    )

    name: Mapped[str] = Fields.name(unique=False)
    code: Mapped[str] = Fields.string_10(unique=False)
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
        argument="AssocCategoryDiscount",
        back_populates="discount",
        foreign_keys="AssocCategoryDiscount.discount_id",
        cascade_soft_delete=True,
    )
    discount_customers: Mapped[list[AssocCustomerDiscount]] = Fields.relationship(
        argument="AssocCustomerDiscount",
        back_populates="discount",
        foreign_keys="AssocCustomerDiscount.discount_id",
        cascade_soft_delete=True,
    )
    discount_items: Mapped[list[AssocItemDiscount]] = Fields.relationship(
        argument="AssocItemDiscount",
        back_populates="discount",
        foreign_keys="AssocItemDiscount.discount_id",
        cascade_soft_delete=True,
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
