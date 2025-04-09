from pydantic import Field

from schemas.base import BaseCreateSchema


class AssocUserGroupCreate(BaseCreateSchema):
    user_id: int = Field(ge=1)
    group_id: int = Field(ge=1)
