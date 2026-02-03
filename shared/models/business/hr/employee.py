from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Index, literal_column, select, text
from sqlalchemy.orm import Mapped, column_property

from models.base.base_model import BaseModel
from models.base.fields import Fields
from models.core import User

if TYPE_CHECKING:
    from models.business.hr.department import Department
    from models.business.hr.position import Position


class Employee(BaseModel):
    __tablename__ = "employees"
    __table_args__ = (Index("ux_employee_pesel_active_true", "pesel", unique=True, postgresql_where=text("is_active")), Index("ux_employee_passport_number_active_true", "passport_number", unique=True, postgresql_where=text("is_active")), Index("ux_employee_id_card_number_active_true", "id_card_number", unique=True, postgresql_where=text("is_active")), Index("ux_employee_email_active_true", "email", unique=True, postgresql_where=text("is_active")), Index("ux_employee_phone_number_active_true", "phone_number", unique=True, postgresql_where=text("is_active")),)

    first_name: Mapped[str] = Fields.string_50()
    middle_name: Mapped[str | None] = Fields.string_50(nullable=True)
    last_name: Mapped[str] = Fields.string_50()

    pesel: Mapped[str | None] = Fields.pesel(unique=False)
    birth_date: Mapped[date] = Fields.date()
    birth_place: Mapped[str] = Fields.string_50()

    passport_number: Mapped[str | None] = Fields.id_document(nullable=True, unique=False)
    passport_expiry: Mapped[date | None] = Fields.date(nullable=True)
    id_card_number: Mapped[str | None] = Fields.id_document(nullable=True, unique=False)
    id_card_expiry: Mapped[date | None] = Fields.date(nullable=True)

    email: Mapped[str | None] = Fields.string_100(unique=False, nullable=True)
    phone_number: Mapped[str] = Fields.string_20(unique=False)

    hire_date: Mapped[date] = Fields.date()
    termination_date: Mapped[date | None] = Fields.date(nullable=True)
    salary: Mapped[int] = Fields.integer()
    is_remote: Mapped[bool] = Fields.boolean(default=False)

    street: Mapped[str | None] = Fields.string_50(nullable=True)
    house_number: Mapped[str] = Fields.string_10()
    apartment_number: Mapped[str | None] = Fields.string_10(nullable=True)
    postal_code: Mapped[str] = Fields.postal_code()
    city: Mapped[str] = Fields.string_50()
    country: Mapped[str] = Fields.string_50()

    bank_account: Mapped[str] = Fields.bank_account()
    bank_swift: Mapped[str] = Fields.bank_swift()
    bank_name: Mapped[str] = Fields.string_50()

    manager_id: Mapped[int | None] = Fields.foreign_key(column="employees.id", nullable=True)
    manager: Mapped[Employee | None] = Fields.relationship(
        argument="Employee", back_populates="subordinates", foreign_keys=[manager_id], remote_side="Employee.id"
    )
    subordinates: Mapped[list[Employee]] = Fields.relationship(
        argument="Employee", back_populates="manager", foreign_keys="Employee.manager_id"
    )

    position_id: Mapped[int] = Fields.foreign_key(column="positions.id")
    position: Mapped[Position] = Fields.relationship(
        argument="Position", back_populates="employees", foreign_keys=[position_id]
    )

    department_id: Mapped[int] = Fields.foreign_key(column="departments.id")
    department: Mapped[Department] = Fields.relationship(
        argument="Department", back_populates="employees", foreign_keys=[department_id]
    )

    user_id: Mapped[int | None] = column_property(
        select(User.id)
        .where(User.employee_id == literal_column("employees.id"))
        .where(User.is_active.is_(True))
        .scalar_subquery()
    )
    user: Mapped[User | None] = Fields.relationship(
        argument="User", back_populates="employee", foreign_keys="User.employee_id", uselist=False
    )
