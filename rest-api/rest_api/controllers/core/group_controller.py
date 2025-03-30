from typing import Callable, List

from fastapi import status

from config import Context
from controllers.base import BaseController
from entities.core import Group
from schemas.core import GroupResponse
from services.core import GroupService


class GroupController(BaseController):
    _service = GroupService()
    _response_schema = GroupResponse
    _entity = Group

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.router.add_api_route(
            "", self.get_all, methods=["GET"], response_model=List[GroupResponse]
        )
        self.router.add_api_route(
            self._id_path, self.get_by_id, methods=["GET"], response_model=GroupResponse
        )
        self.router.add_api_route(
            "",
            self.create,
            methods=["POST"],
            response_model=GroupResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            self._id_path, self.update, methods=["PUT"], response_model=GroupResponse
        )
        self.router.add_api_route(
            self._id_path,
            self.delete,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
