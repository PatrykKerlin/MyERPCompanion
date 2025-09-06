from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from ..trade.order import Order
    from .carrier import Carrier
    from .unit import Unit


class DeliveryMethod(BaseModel):
    __tablename__ = "delivery_methods"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    price_per_unit: Mapped[float] = Fields.numeric_10_2()

    max_width: Mapped[float] = Fields.numeric_6_3()
    max_height: Mapped[float] = Fields.numeric_6_3()
    max_length: Mapped[float] = Fields.numeric_6_3()
    max_weight: Mapped[float] = Fields.numeric_10_3()

    carrier_id: Mapped[int] = Fields.foreign_key(column="cariers.id")
    carrier: Mapped[Carrier] = Fields.relationship(
        argument="Carrier", back_populates="carriers", foreign_keys=[carrier_id]
    )

    unit_id: Mapped[int] = Fields.foreign_key(column="units.id")
    unit: Mapped[Unit] = Fields.relationship(argument="Unit", back_populates="delivery_methods", foreign_keys=[unit_id])

    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="delivery_method", foreign_keys="Order.id"
    )
