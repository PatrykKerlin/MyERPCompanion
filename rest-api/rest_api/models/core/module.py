from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_module_group import AssocModuleGroup
    from .group import Group
    from .view import View


class Module(BaseModel):
    __tablename__ = "modules"

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer(unique=True)

    views: Mapped[list[View]] = Fields.relationship(
        argument="View", back_populates="module", foreign_keys="View.module_id"
    )
    module_groups: Mapped[list[AssocModuleGroup]] = Fields.relationship(
        argument="AssocModuleGroup", back_populates="module", foreign_keys="AssocModuleGroup.module_id"
    )

    @property
    def groups(self) -> list[Group]:
        return [row.group for row in self.module_groups]
