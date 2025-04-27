from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema


class AssocGroupModuleInputSchema(BaseInputSchema):
    group_id: Annotated[int, Field(ge=1)]
    module_id: Annotated[int, Field(ge=1)]


class AssocUserGroupInputSchema(BaseInputSchema):
    user_id: Annotated[int, Field(ge=1)]
    group_id: Annotated[int, Field(ge=1)]
