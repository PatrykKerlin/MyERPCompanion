from pydantic import Field

from schemas.base import BaseCreateSchema


class AssocGroupModuleCreate(BaseCreateSchema):
    group_id: int = Field(ge=1)
    module_id: int = Field(ge=1)
