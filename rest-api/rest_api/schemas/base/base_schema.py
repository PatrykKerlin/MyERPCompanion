from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


class BaseCreateSchema(BaseSchema):
    pass


class BaseResponseSchema(BaseSchema):
    id: int
