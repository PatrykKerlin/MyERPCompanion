from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.business.hr.employee import Employee
    from models.business.hr.position import Position


class Department(BaseModel):
    __tablename__ = "departments"
    __table_args__ = (
        Index("ux_department_name_active_true", "name", unique=True, postgresql_where=text("is_active")),
        Index("ux_department_email_active_true", "email", unique=True, postgresql_where=text("is_active")),
    )

    name: Mapped[str] = Fields.name(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    code: Mapped[str] = Fields.symbol()
    email: Mapped[str | None] = Fields.string_100(unique=False)
    phone_number: Mapped[str | None] = Fields.string_20()

    positions: Mapped[list[Position]] = Fields.relationship(
        argument="Position",
        back_populates="department",
        foreign_keys="Position.department_id",
        cascade_soft_delete=True,
    )

    employees: Mapped[list[Employee]] = Fields.relationship(
        argument="Employee",
        back_populates="department",
        foreign_keys="Employee.department_id",
        cascade_soft_delete=True,
    )
