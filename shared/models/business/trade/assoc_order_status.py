from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.order import Order
    from models.business.trade.status import Status


class AssocOrderStatus(BaseModel):
    __tablename__ = "order_statuses"
    __table_args__ = (
        Index(
            "uq_order_statuses_order_status_active_true",
            "order_id",
            "status_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    order_id: Mapped[int] = Fields.foreign_key(column="orders.id")
    order: Mapped[Order] = Fields.relationship(
        argument="Order", back_populates="order_statuses", foreign_keys=[order_id], cascade_soft_delete=False
    )

    status_id: Mapped[int] = Fields.foreign_key(column="statuses.id")
    status: Mapped[Status] = Fields.relationship(
        argument="Status", back_populates="status_orders", foreign_keys=[status_id], cascade_soft_delete=False
    )
