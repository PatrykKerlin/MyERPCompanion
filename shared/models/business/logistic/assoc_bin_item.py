from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.bin import Bin
    from models.business.logistic.item import Item


class AssocBinItem(BaseModel):
    __tablename__ = "bin_items"
    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "bin_id",
            name="uq_bin_items_item_bin",
        ),
    )

    quantity: Mapped[int] = Fields.integer()

    bin_id: Mapped[int] = Fields.foreign_key(column="bins.id")
    bin: Mapped[Bin] = Fields.relationship(
        argument="Bin", back_populates="bin_items", foreign_keys=[bin_id], cascade_soft_delete=False
    )

    item_id: Mapped[int] = Fields.foreign_key(column="items.id")
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_bins", foreign_keys=[item_id], cascade_soft_delete=False
    )
