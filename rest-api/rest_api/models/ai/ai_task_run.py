from __future__ import annotations

from datetime import date, datetime

from models.base.base_model import BaseModel
from sqlalchemy import Date, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class AiTaskRun(BaseModel):
    __tablename__ = "ai_task_runs"

    task_key: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_range_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_range_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
