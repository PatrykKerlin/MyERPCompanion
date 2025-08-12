from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .bin import Bin


class Warehouse(BaseModel):
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(25), unique=True, nullable=True)

    street: Mapped[str | None] = mapped_column(String(50), nullable=True)
    house_number: Mapped[str] = mapped_column(String(10), nullable=False)
    apartment_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    bins: Mapped[list[Bin]] = relationship(argument="Bin", back_populates="warehouse", foreign_keys="Bin.warehouse_id")
