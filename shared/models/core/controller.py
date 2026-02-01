from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.assoc_view_controller import AssocViewController
    from models.core.view import View


class Controller(BaseModel):
    __tablename__ = "controllers"

    name: Mapped[str] = Fields.name(unique=True)
    table: Mapped[str] = Fields.string_50(nullable=True)
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    controller_views: Mapped[list[AssocViewController]] = Fields.relationship(
        argument="AssocViewController",
        back_populates="controller",
        foreign_keys="AssocViewController.controller_id",
        cascade_soft_delete=True,
    )
