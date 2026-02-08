from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.hr.employee import Employee
    from models.business.logistic.warehouse import Warehouse
    from models.business.trade.customer import Customer
    from models.core.assoc_user_group import AssocUserGroup
    from models.core.group import Group
    from models.core.language import Language


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = (Index("ux_user_username_active_true", "username", unique=True, postgresql_where=text("is_active")), Index("ux_user_employee_id_active_true", "employee_id", unique=True, postgresql_where=text("is_active")),)

    username: Mapped[str] = Fields.string_20(unique=False)
    is_superuser: Mapped[bool] = Fields.boolean(default=False)
    password: Mapped[str] = Fields.string_100()
    theme: Mapped[str] = Fields.string_10()

    employee_id: Mapped[int | None] = Fields.foreign_key(column="employees.id", unique=False, nullable=True)
    employee: Mapped[Employee | None] = Fields.relationship(
        argument="Employee", back_populates="user", foreign_keys=[employee_id], uselist=False
    )

    customer_id: Mapped[int | None] = Fields.foreign_key(column="customers.id", unique=False, nullable=True)
    customer: Mapped[Customer | None] = Fields.relationship(
        argument="Customer", back_populates="user", foreign_keys=[customer_id], uselist=False
    )

    language_id: Mapped[int | None] = Fields.foreign_key(column="languages.id", nullable=True)
    language: Mapped[Language | None] = Fields.relationship(
        argument="Language", back_populates="users", foreign_keys=[language_id]
    )

    warehouse_id: Mapped[int | None] = Fields.foreign_key(column="warehouses.id", unique=False, nullable=True)
    warehouse: Mapped[Warehouse | None] = Fields.relationship(
        argument="Warehouse",
        back_populates="users",
        foreign_keys=[warehouse_id],
        uselist=False,
    )

    user_groups: Mapped[list[AssocUserGroup]] = Fields.relationship(
        argument="AssocUserGroup",
        back_populates="user",
        foreign_keys="AssocUserGroup.user_id",
        cascade_soft_delete=True,
    )

    @property
    def groups(self) -> list[Group]:
        return [row.group for row in self.user_groups]
