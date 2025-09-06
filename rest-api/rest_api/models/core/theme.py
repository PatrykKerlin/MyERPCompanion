from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped

from models.base import BaseModel, Fields

if TYPE_CHECKING:
    from .user import User


class Theme(BaseModel):
    __tablename__ = "themes"

    key: Mapped[str] = Fields.key()

    users: Mapped[list[User]] = Fields.relationship(
        argument="User", back_populates="theme", foreign_keys="User.theme_id"
    )
