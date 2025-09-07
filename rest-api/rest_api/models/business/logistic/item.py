from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from ...core.image import Image
    from ..trade.assoc_item_discount import AssocItemDiscount
    from ..trade.assoc_order_item import AssocOrderItem
    from ..trade.currency import Currency
    from ..trade.discount import Discount
    from ..trade.order import Order
    from ..trade.supplier import Supplier
    from .assoc_bin_item import AssocBinItem
    from .bin import Bin
    from .category import Category
    from .unit import Unit


class Item(BaseModel):
    __tablename__ = "items"

    index: Mapped[str] = Fields.string_10(unique=True, nullable=False)
    name: Mapped[str] = Fields.string_100()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    ean: Mapped[str] = Fields.ean()

    purchase_price: Mapped[float] = Fields.numeric_10_2()
    vat_rate: Mapped[float] = Fields.numeric_3_2()
    margin: Mapped[float] = Fields.numeric_6_3()

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

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="items", foreign_keys=[currency_id]
    )

    category_id: Mapped[int] = Fields.foreign_key(column="categories.id")
    category: Mapped[Category] = Fields.relationship(
        argument="Category", back_populates="items", foreign_keys=[category_id]
    )

    unit_id: Mapped[int] = Fields.foreign_key(column="units.id")
    unit: Mapped[Unit] = Fields.relationship(argument="Unit", back_populates="items", foreign_keys=[unit_id])

    supplier_id: Mapped[int] = Fields.foreign_key(column="suppliers.id")
    supplier: Mapped[Supplier] = Fields.relationship(
        argument="Supplier", back_populates="items", foreign_keys=[supplier_id]
    )

    images: Mapped[list[Image]] = Fields.relationship(
        argument="Image", back_populates="item", foreign_keys="Image.item_id"
    )

    item_bins: Mapped[list[AssocBinItem]] = Fields.relationship(
        argument="AssocBinItem", back_populates="item", foreign_keys="AssocBinItem.item_id"
    )
    item_discounts: Mapped[list[AssocItemDiscount]] = Fields.relationship(
        argument="AssocItemDiscount", back_populates="item", foreign_keys="AssocItemDiscount.item_id"
    )
    item_orders: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem", back_populates="item", foreign_keys="AssocOrderItem.item_id"
    )

    @property
    def bins(self) -> list[Bin]:
        return [row.bin for row in self.item_bins]

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.item_discounts]

    @property
    def orders(self) -> list[Order]:
        return [row.order for row in self.item_orders]
