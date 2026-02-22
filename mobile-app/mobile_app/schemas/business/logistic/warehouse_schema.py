from datetime import datetime
from typing import Annotated

from pydantic import Field
from schemas.base.base_schema import BasePlainSchema, BaseSchema


class WarehouseLoginOptionSchema(BasePlainSchema):
    name: str

    is_active: Annotated[bool, Field(exclude=True)]
    created_at: Annotated[datetime, Field(exclude=True)]
    created_by: Annotated[int, Field(exclude=True)]
    modified_at: Annotated[datetime | None, Field(exclude=True)] = None
    modified_by: Annotated[int | None, Field(exclude=True)] = None
    created_by_username: Annotated[str | None, Field(exclude=True)] = None
    modified_by_username: Annotated[str | None, Field(exclude=True)] = None


class WarehouseLoginOptionFetchSchema(BaseSchema):
    id: int
    name: str
