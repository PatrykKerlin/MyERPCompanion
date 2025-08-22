from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_bin_item import AssocBinItem
    from .item import Item
    from .warehouse import Warehouse


class Bin(BaseModel):
    __tablename__ = "bins"
    __table_args__ = (
        CheckConstraint(
            "(is_inbound IS NULL AND is_outbound IS NOT NULL) OR (is_inbound IS NOT NULL AND is_outbound IS NULL)",
            name="chk_bin_flags",
        ),
    )

    location: Mapped[str] = Fields.string_10(unique=True)
    is_inbound: Mapped[bool] = Fields.boolean(default=False)
    is_outbound: Mapped[bool] = Fields.boolean(default=False)

    max_volume: Mapped[float] = Fields.numeric_10_2()
    max_weight: Mapped[int] = Fields.integer()

    warehouse_id: Mapped[int] = Fields.foreign_key(column="warehouses.id")
    warehouse: Mapped[Warehouse] = Fields.relationship(
        argument="Warehouse", back_populates="bins", foreign_keys=[warehouse_id]
    )

    bin_items: Mapped[list[AssocBinItem]] = Fields.relationship(
        argument="AssocBinItem", back_populates="bin", foreign_keys="AssocBinItem.bin_id"
    )

    @property
    def items(self) -> list[Item]:
        return [row.item for row in self.bin_items]
