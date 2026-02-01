from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.hr.employee import Employee
    from models.business.trade.customer import Customer
    from models.core.assoc_user_group import AssocUserGroup
    from models.core.group import Group
    from models.core.language import Language


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = Fields.string_20(unique=True)
    is_superuser: Mapped[bool] = Fields.boolean(default=False)
    password: Mapped[str] = Fields.string_100()
    theme: Mapped[str] = Fields.string_10()

    employee_id: Mapped[int | None] = Fields.foreign_key(column="employees.id", unique=True, nullable=True)
    employee: Mapped[Employee | None] = Fields.relationship(
        argument="Employee", back_populates="user", foreign_keys=[employee_id], uselist=False
    )

    customer: Mapped[Customer | None] = Fields.relationship(
        argument="Customer", back_populates="user", foreign_keys="Customer.user_id", uselist=False
    )

    language_id: Mapped[int | None] = Fields.foreign_key(column="languages.id", nullable=True)
    language: Mapped[Language | None] = Fields.relationship(
        argument="Language", back_populates="users", foreign_keys=[language_id]
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
