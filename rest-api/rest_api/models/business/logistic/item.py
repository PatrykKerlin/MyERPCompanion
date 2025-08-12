from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Boolean, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .bin_item import BinItem
    from .bin import Bin
    from .category import Category
    from .package import Package
    from .unit import Unit
    from .supplier import Supplier
    from ..sales.item_discount import ItemDiscount
    from ..sales.discount import Discount


class Item(BaseModel):
    __tablename__ = "items"

    index: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    ean: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    purchase_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sales_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    percent: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    margin: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)

    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_fragile: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    min_stock_level: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moq: Mapped[int] = mapped_column(Integer, nullable=False)

    package_id: Mapped[int] = mapped_column(Integer, ForeignKey("packages.id"), nullable=False)
    package: Mapped[Package] = relationship(argument="Package", back_populates="items", foreign_keys=[package_id])

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    category: Mapped[Category] = relationship(argument="Category", back_populates="items", foreign_keys=[category_id])

    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id"), nullable=False)
    unit: Mapped[Unit] = relationship(argument="Unit", back_populates="items", foreign_keys=[unit_id])

    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier: Mapped[Supplier] = relationship(argument="Supplier", back_populates="items", foreign_keys=[supplier_id])

    item_bins: Mapped[list[BinItem]] = relationship(
        argument="BinItem", back_populates="item", foreign_keys="BinItem.item_id"
    )
    item_discounts: Mapped[list[ItemDiscount]] = relationship(
        argument="ItemDiscount", back_populates="item", foreign_keys="ItemDiscount.item_id"
    )

    @property
    def bins(self) -> list[Bin]:
        return [row.bin for row in self.item_bins]

    @property
    def discounts(self) -> list[Discount]:
        return [row.discount for row in self.item_discounts]
