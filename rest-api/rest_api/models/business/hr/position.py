from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .department import Department
    from .employee import Employee


class Position(BaseModel):
    __tablename__ = "positions"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    min_salary: Mapped[int] = mapped_column(Integer, nullable=False)
    max_salary: Mapped[int] = mapped_column(Integer, nullable=False)

    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    department: Mapped[Department] = relationship(
        argument="Department", back_populates="positions", foreign_keys=[department_id]
    )

    employees: Mapped[list[Employee]] = relationship(
        argument="Employee", back_populates="position", foreign_keys="Employee.position_id"
    )
