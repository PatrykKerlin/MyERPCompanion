from schemas.base import BaseStrictSchema
from schemas.validation import Constraints


class AuthStrictSchema(BaseStrictSchema):
    username: Constraints.Username
    password: Constraints.Password
