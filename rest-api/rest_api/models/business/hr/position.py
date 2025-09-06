from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .department import Department
    from .employee import Employee


class Position(BaseModel):
    __tablename__ = "positions"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    level: Mapped[int] = Fields.integer()
    min_salary: Mapped[int] = Fields.integer()
    max_salary: Mapped[int] = Fields.integer()

    department_id: Mapped[int] = Fields.foreign_key(column="departments.id")
    department: Mapped[Department] = Fields.relationship(
        argument="Department", back_populates="positions", foreign_keys=[department_id]
    )

    employees: Mapped[list[Employee]] = Fields.relationship(
        argument="Employee", back_populates="position", foreign_keys="Employee.position_id"
    )
