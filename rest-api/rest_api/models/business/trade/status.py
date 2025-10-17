from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.trade.assoc_order_status import AssocOrderStatus
    from models.business.trade.order import Order


class Status(BaseModel):
    __tablename__ = "statuses"

    name: Mapped[str] = Fields.name()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    step_number: Mapped[int] = Fields.integer(unique=True)

    status_orders: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus", back_populates="status", foreign_keys="AssocOrderStatus.status_id"
    )

    @property
    def orders(self) -> list[Order]:
        return [row.order for row in self.status_orders]
