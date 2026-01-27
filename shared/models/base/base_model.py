from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func, select
from sqlalchemy.orm import Mapped, column_property, declared_attr, mapped_column
from sqlalchemy.sql import column, table

from models.base.base import Base


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    modified_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def created_by_username(cls) -> Mapped[str | None]:
        users_table = table("users", column("id"), column("username"))
        return column_property(
            select(users_table.c.username).where(users_table.c.id == cls.created_by).scalar_subquery()
        )

    @declared_attr
    def modified_by_username(cls) -> Mapped[str | None]:
        users_table = table("users", column("id"), column("username"))
        return column_property(
            select(users_table.c.username).where(users_table.c.id == cls.modified_by).scalar_subquery()
        )
