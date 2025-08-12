from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .employee import Employee
    from .position import Position


class Department(BaseModel):
    __tablename__ = "departments"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    positions: Mapped[list[Position]] = relationship(
        argument="Position", back_populates="department", foreign_keys="Position.department_id"
    )

    employees: Mapped[list[Employee]] = relationship(
        argument="Employee", back_populates="department", foreign_keys="Employee.department_id"
    )
