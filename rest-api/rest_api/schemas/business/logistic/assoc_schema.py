from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema


class AssocBinItemStrictSchema(BaseStrictSchema):
    quantity: Annotated[int, Field(ge=1)]
    item_id: Annotated[int, Field(ge=1)]
    bin_id: Annotated[int, Field(ge=1)]
