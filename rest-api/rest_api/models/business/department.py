from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_employee_department import AssocEmployeeDepartment
    from .employee import Employee


class Department(BaseModel):
    __tablename__ = "departments"

    key: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    employee_departments: Mapped[list[AssocEmployeeDepartment]] = relationship(
        argument="AssocEmployeeDepartment",
        back_populates="department",
        foreign_keys="AssocEmployeeDepartment.department_id",
    )

    @property
    def employees(self) -> list[Employee]:
        return [assoc.employee for assoc in self.employee_departments]
