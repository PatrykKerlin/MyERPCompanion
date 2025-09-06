from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .order import Order
    from .status import Status


class AssocOrderStatus(BaseModel):
    __tablename__ = "order_statuses"

    order_id: Mapped[int] = Fields.foreign_key(column="orders.id", primary_key=True)
    order: Mapped[Order] = Fields.relationship(
        argument="Order", back_populates="order_statuses", foreign_keys=[order_id], cascade_soft_delete=False
    )

    status_id: Mapped[int] = Fields.foreign_key(column="statuses.id", primary_key=True)
    status: Mapped[Status] = Fields.relationship(
        argument="Status", back_populates="status_orders", foreign_keys=[status_id], cascade_soft_delete=False
    )
