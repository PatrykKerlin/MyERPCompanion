from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import func, select, Index, text
from sqlalchemy.orm import Mapped, object_session

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.assoc_bin_item import AssocBinItem
    from models.business.logistic.category import Category
    from models.business.logistic.unit import Unit
    from models.business.trade.assoc_item_discount import AssocItemDiscount
    from models.business.trade.assoc_order_item import AssocOrderItem
    from models.business.trade.order import Order
    from models.business.trade.supplier import Supplier
    from models.core.image import Image


class Item(BaseModel):
    __tablename__ = "items"
    __table_args__ = (Index("ux_item_index_active_true", "index", unique=True, postgresql_where=text("is_active")), Index("ux_item_name_active_true", "name", unique=True, postgresql_where=text("is_active")), Index("ux_item_ean_active_true", "ean", unique=True, postgresql_where=text("is_active")),)

    index: Mapped[str] = Fields.string_10(unique=False, nullable=False)
    name: Mapped[str] = Fields.name(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    ean: Mapped[str] = Fields.ean(unique=False)

    purchase_price: Mapped[float] = Fields.numeric_10_2()
    vat_rate: Mapped[float] = Fields.numeric_3_2()
    margin: Mapped[float] = Fields.numeric_6_3()
    lead_time: Mapped[int] = Fields.integer()

    is_available: Mapped[bool] = Fields.boolean(default=True)
    is_fragile: Mapped[bool] = Fields.boolean(default=False)
    is_package: Mapped[bool] = Fields.boolean(default=False)
    is_returnable: Mapped[bool] = Fields.boolean(default=False)

    expiration_date: Mapped[date | None] = Fields.date(nullable=True)

    width: Mapped[float] = Fields.numeric_6_3()
    height: Mapped[float] = Fields.numeric_6_3()
    length: Mapped[float] = Fields.numeric_6_3()
    weight: Mapped[float] = Fields.numeric_6_3()

    stock_quantity: Mapped[int] = Fields.integer()
    min_stock_level: Mapped[int] = Fields.integer()
    max_stock_level: Mapped[int | None] = Fields.integer(nullable=True)
    moq: Mapped[int] = Fields.integer()

    category_id: Mapped[int] = Fields.foreign_key(column="categories.id")
    category: Mapped[Category] = Fields.relationship(
        argument="Category", back_populates="items", foreign_keys=[category_id], cascade_soft_delete=False
    )

    unit_id: Mapped[int] = Fields.foreign_key(column="units.id")
    unit: Mapped[Unit] = Fields.relationship(
        argument="Unit", back_populates="items", foreign_keys=[unit_id], cascade_soft_delete=False
    )

    supplier_id: Mapped[int] = Fields.foreign_key(column="suppliers.id")
    supplier: Mapped[Supplier] = Fields.relationship(
        argument="Supplier", back_populates="items", foreign_keys=[supplier_id], cascade_soft_delete=False
    )

    images: Mapped[list[Image]] = Fields.relationship(
        argument="Image",
        back_populates="item",
        foreign_keys="Image.item_id",
        cascade_soft_delete=True,
    )

    item_bins: Mapped[list[AssocBinItem]] = Fields.relationship(
        argument="AssocBinItem",
        back_populates="item",
        foreign_keys="AssocBinItem.item_id",
        cascade_soft_delete=True,
    )
    item_discounts: Mapped[list[AssocItemDiscount]] = Fields.relationship(
        argument="AssocItemDiscount",
        back_populates="item",
        foreign_keys="AssocItemDiscount.item_id",
        cascade_soft_delete=True,
    )
    item_orders: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="item",
        foreign_keys="AssocOrderItem.item_id",
        cascade_soft_delete=True,
    )

    @property
    def bin_ids(self) -> list[int]:
        return [row.bin_id for row in self.item_bins]

    @property
    def discount_ids(self) -> list[int]:
        return [row.discount_id for row in self.item_discounts]