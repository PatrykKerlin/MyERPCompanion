from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.business.logistic.bin import Bin
    from models.core.user import User


class Warehouse(BaseModel):
    __tablename__ = "warehouses"
    __table_args__ = (
        Index("ux_warehouse_name_active_true", "name", unique=True, postgresql_where=text("is_active")),
        Index("ux_warehouse_email_active_true", "email", unique=True, postgresql_where=text("is_active")),
        Index("ux_warehouse_phone_number_active_true", "phone_number", unique=True, postgresql_where=text("is_active")),
    )

    name: Mapped[str] = Fields.name(unique=False)
    email: Mapped[str] = Fields.string_100(unique=False)
    phone_number: Mapped[str] = Fields.string_20(unique=False)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    bins: Mapped[list[Bin]] = Fields.relationship(
        argument="Bin",
        back_populates="warehouse",
        foreign_keys="Bin.warehouse_id",
        cascade_soft_delete=True,
    )

    users: Mapped[list[User]] = Fields.relationship(
        argument="User",
        back_populates="warehouse",
        foreign_keys="User.warehouse_id",
    )
