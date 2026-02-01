from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.group import Group
    from models.core.user import User


class AssocUserGroup(BaseModel):
    __tablename__ = "user_groups"
    __table_args__ = (Index(
        "ux_user_groups_user_group_active_true",
        "user_id",
        "group_id",
        unique=True,
        postgresql_where=text("is_active"),),
    )

    group_id: Mapped[int] = Fields.foreign_key(column="groups.id")
    group: Mapped[Group] = Fields.relationship(
        argument="Group", back_populates="group_users", foreign_keys=[group_id], cascade_soft_delete=False
    )

    user_id: Mapped[int] = Fields.foreign_key(column="users.id")
    user: Mapped[User] = Fields.relationship(
        argument="User", back_populates="user_groups", foreign_keys=[user_id], cascade_soft_delete=False
    )
