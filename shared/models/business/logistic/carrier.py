from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.delivery_method import DeliveryMethod
    from models.business.trade.currency import Currency


class Carrier(BaseModel):
    __tablename__ = "carriers"
    __table_args__ = (Index("ux_carrier_name_active_true", "name", unique=True, postgresql_where=text("is_active")),)

    name: Mapped[str] = Fields.name(unique=False)

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
        argument="Currency", back_populates="carriers", foreign_keys=[currency_id], cascade_soft_delete=False
    )

    delivery_methods: Mapped[list[DeliveryMethod]] = Fields.relationship(
        argument="DeliveryMethod",
        back_populates="carrier",
        foreign_keys="DeliveryMethod.carrier_id",
        cascade_soft_delete=True,
    )
