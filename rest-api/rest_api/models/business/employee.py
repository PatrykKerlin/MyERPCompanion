from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

if TYPE_CHECKING:
    from .assoc_employee_department import AssocEmployeeDepartment
    from .department import Department
    from ..core.user import User


class Employee(BaseModel):
    __tablename__ = "employees"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    user: Mapped[User | None] = relationship(
        argument="User", back_populates="employee", foreign_keys="User.employee_id", uselist=False
    )

    employee_departments: Mapped[list[AssocEmployeeDepartment]] = relationship(
        argument="AssocEmployeeDepartment",
        back_populates="employee",
        foreign_keys="AssocEmployeeDepartment.employee_id",
    )

    @property
    def departments(self) -> list[Department]:
        return [assoc.department for assoc in self.employee_departments]
