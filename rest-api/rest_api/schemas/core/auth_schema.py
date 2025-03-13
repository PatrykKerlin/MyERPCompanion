from pydantic import BaseModel, Field, constr


class AuthSchema(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(...)
    password: constr(min_length=5, max_length=128) = Field(...)

    class Config:
        from_attributes = True
