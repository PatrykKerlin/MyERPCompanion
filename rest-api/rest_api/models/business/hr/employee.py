from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from ...core.user import User
    from .department import Department
    from .position import Position


class Employee(BaseModel):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint(
            "(passport_number IS NULL AND passport_expiry IS NULL) OR "
            "(passport_number IS NOT NULL AND passport_expiry IS NOT NULL)",
            name="chk_passport_expiry_required",
        ),
        CheckConstraint(
            "(id_card_number IS NULL AND id_card_expiry IS NULL) OR "
            "(id_card_number IS NOT NULL AND id_card_expiry IS NOT NULL)",
            name="chk_id_card_expiry_required",
        ),
        CheckConstraint(
            "id_card_number IS NOT NULL OR passport_number IS NOT NULL",
            name="chk_employee_document_required",
        ),
    )

    first_name: Mapped[str] = Fields.string_50()
    middle_name: Mapped[str | None] = Fields.string_50(nullable=True)
    last_name: Mapped[str] = Fields.string_50()

    pesel: Mapped[str | None] = Fields.pesel()
    birth_date: Mapped[date] = Fields.date()
    birth_place: Mapped[str] = Fields.string_50()

    passport_number: Mapped[str | None] = Fields.id_document(nullable=True)
    passport_expiry: Mapped[date | None] = Fields.date(nullable=True)
    id_card_number: Mapped[str | None] = Fields.id_document(nullable=True)
    id_card_expiry: Mapped[date | None] = Fields.date(nullable=True)

    email: Mapped[str | None] = Fields.string_100(unique=True, nullable=True)
    phone_number: Mapped[str] = Fields.string_20(unique=True)

    hire_date: Mapped[date] = Fields.date()
    termination_date: Mapped[date | None] = Fields.date(nullable=True)
    salary: Mapped[int] = Fields.integer()

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

    user: Mapped[User | None] = Fields.relationship(
        argument="User", back_populates="employee", foreign_keys="User.employee_id", uselist=False
    )
