from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime, Integer, ForeignKey, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from ..logistic.supplier import Supplier
    from .customer import Customer
    from .order_item import OrderItem
    from .invoice import Invoice
    from .payment import Payment


class Order(BaseModel):
    __tablename__ = "orders"
