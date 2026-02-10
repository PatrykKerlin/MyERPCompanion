from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.assoc_view_controller import AssocViewController
    from models.core.module import Module


class View(BaseModel):
    __tablename__ = "views"
    __table_args__ = (
        Index(
            "uq_view_module_order_active_true",
            "order",
            "module_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    key: Mapped[str] = Fields.key(unique=False)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer()

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(argument="Module", back_populates="views", foreign_keys=[module_id])

    view_controllers: Mapped[list[AssocViewController]] = Fields.relationship(
        argument="AssocViewController",
        back_populates="view",
        foreign_keys="AssocViewController.view_id",
        cascade_soft_delete=True,
    )

    @property
    def controller_ids(self) -> list[int]:
        return [row.controller_id for row in self.view_controllers]
