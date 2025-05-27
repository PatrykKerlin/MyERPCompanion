from typing import Union

from config import Context
from controllers.base import BaseController
from schemas.core import UserInputCreateSchema, UserInputUpdateSchema, UserOutputSchema
from services.core import UserService


class UserController(
    BaseController[
        UserService,
        Union[UserInputCreateSchema, UserInputUpdateSchema],
        UserOutputSchema,
    ]
):
    _service_cls = UserService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes(UserOutputSchema)
