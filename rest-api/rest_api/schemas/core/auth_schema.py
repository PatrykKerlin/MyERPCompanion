from typing import Annotated

from pydantic import BaseModel, Field


class AuthSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=5, max_length=128)]

    class Config:
        from_attributes = True
