from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Date, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel
from models.base.orm import relationship

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
    )

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    pesel: Mapped[str | None] = mapped_column(String(11), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_place: Mapped[str] = mapped_column(String(50), nullable=False)

    passport_number: Mapped[str | None] = mapped_column(String(9), unique=True, nullable=True)
    passport_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    id_card_number: Mapped[str | None] = mapped_column(String(9), unique=True, nullable=True)
    id_card_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(25), unique=True, nullable=True)

    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary: Mapped[int] = mapped_column(Integer, nullable=False)

    street: Mapped[str | None] = mapped_column(String(50), nullable=True)
    house_number: Mapped[str] = mapped_column(String(10), nullable=False)
    apartment_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    bank_account: Mapped[str] = mapped_column(String(26), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)

    manager_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("employees.id"), nullable=True)
    manager: Mapped[Employee | None] = relationship(
        argument="Employee", back_populates="subordinates", foreign_keys=[manager_id], remote_side="Employee.id"
    )
    subordinates: Mapped[list[Employee]] = relationship(
        argument="Employee", back_populates="manager", foreign_keys="Employee.manager_id"
    )

    position_id: Mapped[int] = mapped_column(Integer, ForeignKey("positions.id"), nullable=False)
    position: Mapped[Position] = relationship(
        argument="Position", back_populates="employees", foreign_keys=[position_id]
    )

    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    department: Mapped[Department] = relationship(
        argument="Department", back_populates="employees", foreign_keys=[department_id]
    )

    user: Mapped[User | None] = relationship(
        argument="User", back_populates="employee", foreign_keys="User.employee_id", uselist=False
    )
