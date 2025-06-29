from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .department import Department
    from .employee import Employee


class AssocEmployeeDepartment(BaseModel):
    __tablename__ = "employees_departments"

    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), primary_key=True)

    department: Mapped[Department] = relationship(
        argument="Department",
        back_populates="employee_departments",
        foreign_keys=[department_id],
        cascade_soft_delete=False,
    )
    employee: Mapped[Employee] = relationship(
        argument="Employee",
        back_populates="employee_departments",
        foreign_keys=[employee_id],
        cascade_soft_delete=False,
    )
