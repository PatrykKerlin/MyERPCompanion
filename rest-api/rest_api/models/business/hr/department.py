from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .employee import Employee
    from .position import Position


class Department(BaseModel):
    __tablename__ = "departments"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    positions: Mapped[list[Position]] = Fields.relationship(
        argument="Position", back_populates="department", foreign_keys="Position.department_id"
    )

    employees: Mapped[list[Employee]] = Fields.relationship(
        argument="Employee", back_populates="department", foreign_keys="Employee.department_id"
    )
