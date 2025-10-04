from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .assoc_user_view import AssocUserView
    from .module import Module


class View(BaseModel):
    __tablename__ = "views"
    __table_args__ = (
        UniqueConstraint("order", "module_id", name="uq_view_module_order"),
        Index("ix_views_controllers_gin", "controllers", postgresql_using="gin"),
    )

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer()
    controllers: Mapped[list[str]] = Fields.string_list()

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(argument="Module", back_populates="views", foreign_keys=[module_id])

    view_users: Mapped[list[AssocUserView]] = Fields.relationship(
        argument="AssocUserView", back_populates="view", foreign_keys="AssocUserView.view_id"
    )
