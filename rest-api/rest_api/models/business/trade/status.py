from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_order_status import AssocOrderStatus
    from .order import Order


class Status(BaseModel):
    __tablename__ = "statuses"

    key: Mapped[str] = Fields.key()
    step_number: Mapped[int] = Fields.integer(unique=True)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    status_orders: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus", back_populates="status", foreign_keys="AssocOrderStatus.status_id"
    )

    @property
    def orders(self) -> list[Order]:
        return [row.order for row in self.status_orders]
