from __future__ import annotations

from typing import TYPE_CHECKING

from models.base.base_model import BaseModel
from models.base.fields import Fields
from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from models.core.group import Group
    from models.core.module import Module


class AssocModuleGroup(BaseModel):
    __tablename__ = "module_groups"
    __table_args__ = (
        Index(
            "uq_module_groups_group_module_active_true",
            "group_id",
            "module_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    can_read: Mapped[bool] = Fields.boolean(default=True)
    can_modify: Mapped[bool] = Fields.boolean(default=False)

    group_id: Mapped[int] = Fields.foreign_key(column="groups.id")
    group: Mapped[Group] = Fields.relationship(
        argument="Group", back_populates="group_modules", foreign_keys=[group_id], cascade_soft_delete=False
    )

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(
        argument="Module", back_populates="module_groups", foreign_keys=[module_id], cascade_soft_delete=False
    )
