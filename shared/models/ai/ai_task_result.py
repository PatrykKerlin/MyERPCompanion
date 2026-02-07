from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base.base_model import BaseModel


class AiTaskResult(BaseModel):
    __tablename__ = "ai_task_results"

    task_key: Mapped[str] = mapped_column(String(50), nullable=False)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_task_runs.id"), nullable=False)
    item_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("customers.id"), nullable=True)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    predicted_at: Mapped[date] = mapped_column(Date, nullable=False)
    horizon_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
