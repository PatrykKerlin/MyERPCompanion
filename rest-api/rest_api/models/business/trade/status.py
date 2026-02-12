from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import CheckConstraint, Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.business.trade.assoc_order_status import AssocOrderStatus


class Status(BaseModel):
    __tablename__ = "statuses"
    __table_args__ = (
        CheckConstraint('"order" <= 10', name="ck_statuses_order_max_10"),
        Index(
            "ux_status_key_active_true",
            "key",
            unique=True,
            postgresql_where=text("is_active"),
        ),
        Index(
            "ux_statuses_order_active_true",
            "order",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    key: Mapped[str] = Fields.key(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer()

    status_orders: Mapped[list[AssocOrderStatus]] = Fields.relationship(
        argument="AssocOrderStatus",
        back_populates="status",
        foreign_keys="AssocOrderStatus.status_id",
        cascade_soft_delete=True,
    )

    @property
    def order_ids(self) -> list[int]:
        return [row.order_id for row in self.status_orders]
