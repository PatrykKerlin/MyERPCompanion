from __future__ import annotations

from datetime import date

from models.base.base_model import BaseModel
from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class SalesForecast(BaseModel):
    __tablename__ = "sales_forecast"

    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_task_runs.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    predicted_at: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    aggregation: Mapped[str] = mapped_column(String(20), nullable=False)
    horizon_months: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_rate_assumption: Mapped[float] = mapped_column(Float, nullable=False)
