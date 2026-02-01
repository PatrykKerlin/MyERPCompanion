from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.controller import Controller
    from models.core.view import View


class AssocViewController(BaseModel):
    __tablename__ = "view_controllers"
    __table_args__ = (Index(
        "ux_view_controllers_view_controller_active_true",
        "view_id",
        "controller_id",
        unique=True,
        postgresql_where=text("is_active"),),
    )

    view_id: Mapped[int] = Fields.foreign_key(column="views.id")
    view: Mapped[View] = Fields.relationship(
        argument="View", back_populates="view_controllers", foreign_keys=[view_id], cascade_soft_delete=False
    )

    controller_id: Mapped[int] = Fields.foreign_key(column="controllers.id")
    controller: Mapped[Controller] = Fields.relationship(
        argument="Controller",
        back_populates="controller_views",
        foreign_keys=[controller_id],
        cascade_soft_delete=False,
    )
