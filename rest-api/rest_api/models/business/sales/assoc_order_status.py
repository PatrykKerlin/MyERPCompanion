from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .order import Order
    from .status import Status


class AssocOrderStatus(BaseModel):
    __tablename__ = "order_statuses"

    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), primary_key=True)
    order: Mapped[Order] = relationship(
        argument="Order", back_populates="order_statuses", foreign_keys=[order_id], cascade_soft_delete=False
    )

    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("statuses.id"), primary_key=True)
    status: Mapped[Status] = relationship(
        argument="Status", back_populates="status_orders", foreign_keys=[status_id], cascade_soft_delete=False
    )
