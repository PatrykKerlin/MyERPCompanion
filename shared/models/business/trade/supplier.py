from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.item import Item
    from models.business.trade.currency import Currency
    from models.business.trade.order import Order


class Supplier(BaseModel):
    __tablename__ = "suppliers"

    company_name: Mapped[str] = Fields.name()

    company_email: Mapped[str | None] = Fields.string_50(nullable=True)
    company_phone: Mapped[str | None] = Fields.string_20(nullable=True)
    company_website: Mapped[str | None] = Fields.string_50(nullable=True)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    contact_person: Mapped[str] = Fields.string_100()
    contact_phone: Mapped[str] = Fields.string_20()
    contact_email: Mapped[str] = Fields.string_100()

    bank_account: Mapped[str] = Fields.bank_account()
    bank_swift: Mapped[str] = Fields.bank_swift()
    bank_name: Mapped[str] = Fields.string_50()
    tax_id: Mapped[str] = Fields.string_10()
    payment_term: Mapped[int] = Fields.integer()

    notes: Mapped[str | None] = Fields.string_1000(nullable=True)

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="suppliers", foreign_keys=[currency_id], cascade_soft_delete=False
    )

    items: Mapped[list[Item]] = Fields.relationship(
        argument="Item", back_populates="supplier", foreign_keys="Item.supplier_id"
    )
    orders: Mapped[list[Order]] = Fields.relationship(
        argument="Order", back_populates="supplier", foreign_keys="Order.supplier_id"
    )
