from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema


class AssocUserGroupCreate(BaseCreateSchema):
    user_id: Annotated[int, Field(ge=1)]
    group_id: Annotated[int, Field(ge=1)]
