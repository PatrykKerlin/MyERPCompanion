from pydantic import BaseModel


class TokenPlainSchema(BaseModel):
    access: str
    refresh: str
