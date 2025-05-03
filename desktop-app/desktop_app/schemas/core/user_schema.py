from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
    language_id: int
    theme_id: int
