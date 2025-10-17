from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.group import Group
    from models.core.module import Module


class AssocModuleGroup(BaseModel):
    __tablename__ = "module_groups"

    group_id: Mapped[int] = Fields.foreign_key(column="groups.id", primary_key=True)
    group: Mapped[Group] = Fields.relationship(
        argument="Group", back_populates="group_modules", foreign_keys=[group_id], cascade_soft_delete=False
    )

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id", primary_key=True)
    module: Mapped[Module] = Fields.relationship(
        argument="Module", back_populates="module_groups", foreign_keys=[module_id], cascade_soft_delete=False
    )
