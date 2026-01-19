from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.carrier import Carrier
    from models.business.logistic.unit import Unit
    from models.business.trade.order import Order


class DeliveryMethod(BaseModel):
    __tablename__ = "delivery_methods"

    name: Mapped[str] = Fields.name()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    price_per_unit: Mapped[float] = Fields.numeric_10_2()

    max_width: Mapped[float] = Fields.numeric_6_3()
    max_height: Mapped[float] = Fields.numeric_6_3()
    max_length: Mapped[float] = Fields.numeric_6_3()
    max_weight: Mapped[float] = Fields.numeric_11_3()

    carrier_id: Mapped[int] = Fields.foreign_key(column="carriers.id")
    carrier: Mapped[Carrier] = Fields.relationship(
        argument="Carrier", back_populates="delivery_methods", foreign_keys=[carrier_id]
    )

    unit_id: Mapped[int] = Fields.foreign_key(column="units.id")
    unit: Mapped[Unit] = Fields.relationship(argument="Unit", back_populates="delivery_methods", foreign_keys=[unit_id])

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="delivery_method", foreign_keys="Order.delivery_method_id"
    )
