from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema


class AssocModuleGroupStrictSchema(BaseStrictSchema):
    group_id: Annotated[int, Field(ge=1)]
    module_id: Annotated[int, Field(ge=1)]


class AssocUserGroupStrictSchema(BaseStrictSchema):
    user_id: Annotated[int, Field(ge=1)]
    group_id: Annotated[int, Field(ge=1)]
