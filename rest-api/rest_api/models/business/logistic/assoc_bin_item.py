from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .bin import Bin
    from .item import Item


class AssocBinItem(BaseModel):
    __tablename__ = "bin_items"

    quantity: Mapped[int] = Fields.integer()

    item_id: Mapped[int] = Fields.foreign_key(column="items.id", primary_key=True)
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="item_bins", foreign_keys=[item_id], cascade_soft_delete=False
    )

    bin_id: Mapped[int] = Fields.foreign_key(column="bins.id", primary_key=True)
    bin: Mapped[Bin] = Fields.relationship(
        argument="Bin", back_populates="bin_items", foreign_keys=[bin_id], cascade_soft_delete=False
    )
