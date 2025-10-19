from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.core.module import Module


class View(BaseModel):
    __tablename__ = "views"
    __table_args__ = (UniqueConstraint("order", "module_id", name="uq_view_module_order"),)

    key: Mapped[str] = Fields.key()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)
    order: Mapped[int] = Fields.integer()

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(argument="Module", back_populates="views", foreign_keys=[module_id])
