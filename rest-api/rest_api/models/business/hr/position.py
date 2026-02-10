from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.hr.department import Department
    from models.business.hr.employee import Employee
    from models.business.trade.currency import Currency


class Position(BaseModel):
    __tablename__ = "positions"
    __table_args__ = (Index("ux_position_name_active_true", "name", unique=True, postgresql_where=text("is_active")),)

    name: Mapped[str] = Fields.name(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    code: Mapped[str] = Fields.symbol()
    level: Mapped[int] = Fields.integer()
    min_salary: Mapped[int] = Fields.integer()
    max_salary: Mapped[int] = Fields.integer()

    currency_id: Mapped[int] = Fields.foreign_key(column="currencies.id")
    currency: Mapped[Currency] = Fields.relationship(
        argument="Currency", back_populates="positions", foreign_keys=[currency_id]
    )

    department_id: Mapped[int] = Fields.foreign_key(column="departments.id")
    department: Mapped[Department] = Fields.relationship(
        argument="Department", back_populates="positions", foreign_keys=[department_id]
    )

    employees: Mapped[list[Employee]] = Fields.relationship(
        argument="Employee",
        back_populates="position",
        foreign_keys="Employee.position_id",
        cascade_soft_delete=True,
    )
