from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_order_status import AssocOrderStatus
    from .order import Order


class Status(BaseModel):
    __tablename__ = "statuses"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status_orders: Mapped[list[AssocOrderStatus]] = relationship(
        argument="AssocOrderStatus", back_populates="status", foreign_keys="AssocOrderStatus.status_id"
    )

    @property
    def orders(self) -> list[Order]:
        return [row.order for row in self.status_orders]
