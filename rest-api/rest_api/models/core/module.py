from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.assoc_module_group import AssocModuleGroup
    from models.core.group import Group
    from models.core.view import View


class Module(BaseModel):
    __tablename__ = "modules"
    __table_args__ = (Index("ix_module_controllers_gin", "controllers", postgresql_using="gin"),)

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    in_side_menu: Mapped[bool] = Fields.boolean(default=True)
    order: Mapped[int] = Fields.integer()
    controllers: Mapped[list[str]] = Fields.string_list()

    views: Mapped[list[View]] = Fields.relationship(
        argument="View", back_populates="module", foreign_keys="View.module_id"
    )
    module_groups: Mapped[list[AssocModuleGroup]] = Fields.relationship(
        argument="AssocModuleGroup", back_populates="module", foreign_keys="AssocModuleGroup.module_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [row.group for row in self.module_groups]
