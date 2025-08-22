from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .module import Module


class View(BaseModel):
    __tablename__ = "views"

    key: Mapped[str] = Fields.key()
    controller: Mapped[str] = Fields.string_50(unique=True)
    path: Mapped[str] = Fields.string_100()
    in_menu: Mapped[bool] = Fields.boolean(default=False)
    order: Mapped[int] = Fields.integer(unique=True)

    module_id: Mapped[int] = Fields.foreign_key(column="modules.id")
    module: Mapped[Module] = Fields.relationship(argument="Module", back_populates="views", foreign_keys=[module_id])
