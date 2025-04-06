# pyright: reportIncompatibleMethodOverride=false

from typing import Callable, List

from fastapi import Request, Response

from config import Context
from controllers.base import BaseController
from schemas.core import EndpointCreate, EndpointResponse
from services.core import EndpointService
from utils import AuthUtil


class EndpointController(
    BaseController[EndpointService, EndpointCreate, EndpointResponse]
):
    _service_cls = EndpointService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes("", "/endpoint_id", EndpointResponse)

    @AuthUtil.restrict_access()
    async def get_all(self, request: Request) -> list[EndpointResponse]:
        return await super().get_all(request)

    @AuthUtil.restrict_access()
    async def get_by_id(self, request: Request, endpoint_id: int) -> EndpointResponse:
        return await super().get_by_id(request, endpoint_id)

    @AuthUtil.restrict_access()
    async def create(self, data: EndpointCreate, request: Request) -> EndpointResponse:
        return await super().create(data, request)

    @AuthUtil.restrict_access()
    async def update(
        self, data: EndpointCreate, request: Request, endpoint_id: int
    ) -> EndpointResponse:
        return await super().update(data, request, endpoint_id)

    @AuthUtil.restrict_access()
    async def delete(self, request: Request, endpoint_id: int) -> Response:
        return await super().delete(request, endpoint_id)
