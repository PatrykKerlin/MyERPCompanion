from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.bin import Bin


class Warehouse(BaseModel):
    __tablename__ = "warehouses"

    name: Mapped[str] = Fields.name()
    email: Mapped[str] = Fields.string_100(unique=True)
    phone_number: Mapped[str] = Fields.string_20(unique=True)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    bins: Mapped[list[Bin]] = Fields.relationship(
        argument="Bin", back_populates="warehouse", foreign_keys="Bin.warehouse_id"
    )
