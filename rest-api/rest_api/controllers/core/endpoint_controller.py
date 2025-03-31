from typing import Callable, List

from fastapi import status

from config import Context
from controllers.base import BaseController
from entities.core import Endpoint
from schemas.core import EndpointResponse
from services.core import EndpointService


class EndpointController(BaseController):
    _service = EndpointService()
    _response_schema = EndpointResponse
    _entity = Endpoint

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.router.add_api_route(
            "", self.get_all, methods=["GET"], response_model=List[EndpointResponse]
        )
        self.router.add_api_route(
            self._id_path, self.get_by_id, methods=["GET"], response_model=EndpointResponse
        )
        self.router.add_api_route(
            "",
            self.create,
            methods=["POST"],
            response_model=EndpointResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            self._id_path, self.update, methods=["PUT"], response_model=EndpointResponse
        )
        self.router.add_api_route(
            self._id_path,
            self.delete,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
