from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.assoc_bin_item import AssocBinItem
    from models.business.logistic.warehouse import Warehouse
    from models.business.trade.assoc_order_item import AssocOrderItem


class Bin(BaseModel):
    __tablename__ = "bins"
    __table_args__ = (Index("ux_bin_location_active_true", "location", unique=True, postgresql_where=text("is_active")),)

    location: Mapped[str] = Fields.string_10(unique=False)
    is_inbound: Mapped[bool] = Fields.boolean(default=False)
    is_outbound: Mapped[bool] = Fields.boolean(default=False)

    max_volume: Mapped[float] = Fields.numeric_10_2()
    max_weight: Mapped[int] = Fields.integer()

    warehouse_id: Mapped[int] = Fields.foreign_key(column="warehouses.id")
    warehouse: Mapped[Warehouse] = Fields.relationship(
        argument="Warehouse", back_populates="bins", foreign_keys=[warehouse_id], cascade_soft_delete=False
    )

    bin_items: Mapped[list[AssocBinItem]] = Fields.relationship(
        argument="AssocBinItem",
        back_populates="bin",
        foreign_keys="AssocBinItem.bin_id",
        cascade_soft_delete=True,
    )

    bin_order_items: Mapped[list[AssocOrderItem]] = Fields.relationship(
        argument="AssocOrderItem",
        back_populates="bin",
        foreign_keys="AssocOrderItem.bin_id",
        cascade_soft_delete=True,
    )

    @property
    def item_ids(self) -> list[int]:
        return [row.item_id for row in self.bin_items]
