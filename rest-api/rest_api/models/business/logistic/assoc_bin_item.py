from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .bin import Bin
    from .item import Item


class AssocBinItem(BaseModel):
    __tablename__ = "bin_items"

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), primary_key=True)
    item: Mapped[Item] = relationship(
        argument="Item", back_populates="item_bins", foreign_keys=[item_id], cascade_soft_delete=False
    )

    bin_id: Mapped[int] = mapped_column(Integer, ForeignKey("bins.id"), primary_key=True)
    bin: Mapped[Bin] = relationship(
        argument="Bin", back_populates="bin_items", foreign_keys=[bin_id], cascade_soft_delete=False
    )
