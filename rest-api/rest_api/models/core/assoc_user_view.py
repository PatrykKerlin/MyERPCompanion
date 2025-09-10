from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .user import User
    from .view import View


class AssocUserView(BaseModel):
    __tablename__ = "user_views"

    can_read: Mapped[bool] = Fields.boolean(default=False)
    can_modify: Mapped[bool] = Fields.boolean(default=False)

    user_id: Mapped[int] = Fields.foreign_key(column="users.id", primary_key=True)
    user: Mapped[User] = Fields.relationship(
        argument="User", back_populates="user_views", foreign_keys=[user_id], cascade_soft_delete=False
    )

    view_id: Mapped[int] = Fields.foreign_key(column="views.id", primary_key=True)
    view: Mapped[View] = Fields.relationship(
        argument="View", back_populates="view_users", foreign_keys=[view_id], cascade_soft_delete=False
    )
