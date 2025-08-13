from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_bin_item import AssocBinItem
    from .item import Item
    from .warehouse import Warehouse


class Bin(BaseModel):
    __tablename__ = "bins"

    location: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    is_inbound: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_outbound: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    max_volume: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_weight: Mapped[int] = mapped_column(Integer, nullable=False)

    warehouse_id: Mapped[Warehouse] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False)
    warehouse: Mapped[Warehouse] = relationship(
        argument="Warehouse", back_populates="bins", foreign_keys=[warehouse_id]
    )

    bin_items: Mapped[list[AssocBinItem]] = relationship(
        argument="AssocBinItem", back_populates="bin", foreign_keys="AssocBinItem.bin_id"
    )

    @property
    def items(self) -> list[Item]:
        return [row.item for row in self.bin_items]
