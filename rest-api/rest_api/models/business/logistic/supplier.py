from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .item import Item


class Supplier(BaseModel):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(25), unique=True, nullable=True)
    website: Mapped[str | None] = mapped_column(String(50), nullable=True)

    street: Mapped[str | None] = mapped_column(String(50), nullable=True)
    house_number: Mapped[str] = mapped_column(String(10), nullable=False)
    apartment_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(25), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(50), nullable=False)

    bank_account: Mapped[str] = mapped_column(String(26), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(10), nullable=False)
    payment_terms: Mapped[int] = mapped_column(Integer, nullable=False)

    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
