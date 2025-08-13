from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_bin_item import AssocBinItem
    from .bin import Bin
    from .category import Category
    from .unit import Unit
    from .supplier import Supplier
    from ..sales.currency import Currency
    from ..sales.discount import Discount
    from ..sales.assoc_item_discount import AssocItemDiscount
    from ..sales.assoc_order_item import AssocOrderItem
    from ..sales.order import Order


class Item(BaseModel):
    __tablename__ = "items"

    index: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    ean: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    purchase_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    vat_rate: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    margin: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)

    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_fragile: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_package: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_returnable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    width: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    height: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    length: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    min_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moq: Mapped[int] = mapped_column(Integer, nullable=False)

    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    currency: Mapped[Currency] = relationship(argument="Currency", back_populates="items", foreign_keys=[currency_id])

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    category: Mapped[Category] = relationship(argument="Category", back_populates="items", foreign_keys=[category_id])

    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"), nullable=False)
    unit: Mapped[Unit] = relationship(argument="Unit", back_populates="items", foreign_keys=[unit_id])

    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier: Mapped[Supplier] = relationship(argument="Supplier", back_populates="items", foreign_keys=[supplier_id])

    item_bins: Mapped[list[AssocBinItem]] = relationship(
        argument="AssocBinItem", back_populates="item", foreign_keys="AssocBinItem.item_id"
    )
    item_discounts: Mapped[list[AssocItemDiscount]] = relationship(
        argument="AssocItemDiscount", back_populates="item", foreign_keys="AssocItemDiscount.item_id"
    )
    item_orders: Mapped[list[AssocOrderItem]] = relationship(
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
