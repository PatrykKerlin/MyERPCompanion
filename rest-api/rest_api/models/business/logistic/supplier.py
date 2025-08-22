from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .item import Item
    from ..trade.order import Order


class Supplier(BaseModel):
    __tablename__ = "suppliers"

    name: Mapped[str] = Fields.string_100()

    email: Mapped[str | None] = Fields.string_50(nullable=True)
    phone_number: Mapped[str | None] = Fields.string_20(nullable=True)
    website: Mapped[str | None] = Fields.string_50(nullable=True)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    first_name: Mapped[str] = Fields.string_50()
    last_name: Mapped[str] = Fields.string_50()
    contact_phone: Mapped[str] = Fields.string_20()
    contact_email: Mapped[str] = Fields.string_100(unique=True)

    bank_account: Mapped[str] = Fields.bank_account()
    bank_name: Mapped[str] = Fields.string_50()
    tax_id: Mapped[str] = Fields.string_10()
    payment_term: Mapped[int] = Fields.integer()

    notes: Mapped[str | None] = Fields.string_1000(nullable=True)

    items: Mapped[list[Item]] = Fields.relationship(
        argument="Item", back_populates="supplier", foreign_keys="Item.supplier_id"
    )
    order: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="supplier", foreign_keys="Order.supplier_id"
    )
