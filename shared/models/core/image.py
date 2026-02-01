from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, text
from sqlalchemy.orm import Mapped

from models.base.base_model import BaseModel
from models.base.fields import Fields

if TYPE_CHECKING:
    from models.business.logistic.item import Item


class Image(BaseModel):
    __tablename__ = "images"
    __table_args__ = (
        Index("uq_item_images_only_one_primary", "item_id", unique=True, postgresql_where=text("is_primary AND is_active")),
    )

    url: Mapped[str] = Fields.string_1000(nullable=False)
    is_primary: Mapped[bool] = Fields.boolean(default=False)
    order: Mapped[int] = Fields.integer()
    description: Mapped[str | None] = Fields.string_1000(nullable=True)

    item_id: Mapped[int] = Fields.foreign_key(column="items.id")
    item: Mapped[Item] = Fields.relationship(
        argument="Item", back_populates="images", foreign_keys=[item_id], cascade_soft_delete=False
    )
