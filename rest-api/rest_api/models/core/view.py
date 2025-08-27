from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .module import Module


class View(BaseModel):
    __tablename__ = "views"
    __table_args__ = (
        UniqueConstraint("order", "module_id", name="uq_view_module_order"),
        Index("ix_views_controllers_gin", "controllers", postgresql_using="gin"),
    )

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    in_menu: Mapped[bool] = Fields.boolean(default=False)
    order: Mapped[int] = Fields.integer()
    controllers: Mapped[list[str]] = Fields.string_list()

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(argument="Module", back_populates="views", foreign_keys=[module_id])
