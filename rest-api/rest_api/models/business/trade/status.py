from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.assoc_order_status import AssocOrderStatus
    from models.business.trade.order import Order


class Status(BaseModel):
    __tablename__ = "statuses"
    __table_args__ = (
        CheckConstraint('"order" <= 9', name="ck_statuses_order_max_9"),
        Index(
            "ux_statuses_order_active_true",
            "order",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer()

    status_orders: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus", back_populates="status", foreign_keys="AssocOrderStatus.status_id"
    )

    @property
    def orders(self) -> list[Order]:
        return [row.order for row in self.status_orders]

    @property
    def order_ids(self) -> list[int]:
        return [row.order.id for row in self.status_orders]
