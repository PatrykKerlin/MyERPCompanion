from schemas.base.base_schema import BaseStrictSchema
from schemas.validation.constraints import Constraints


class AuthStrictSchema(BaseStrictSchema):
    username: Constraints.Username
    password: Constraints.Password
    client: Constraints.AuthClient
