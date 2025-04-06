from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema


class AssocGroupModuleCreate(BaseCreateSchema):
    group_id: Annotated[int, Field(ge=1)]
    module_id: Annotated[int, Field(ge=1)]
