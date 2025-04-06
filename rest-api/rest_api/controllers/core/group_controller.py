# pyright: reportIncompatibleMethodOverride=false

from typing import Callable, List

from fastapi import Request, Response

from config import Context
from controllers.base import BaseController
from schemas.core import GroupCreate, GroupResponse
from services.core import GroupService
from utils import AuthUtil


class GroupController(BaseController[GroupService, GroupCreate, GroupResponse]):
    _service_cls = GroupService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._register_routes("", "/group_id", GroupResponse)

    @AuthUtil.restrict_access()
    async def get_all(self, request: Request) -> list[GroupResponse]:
        return await super().get_all(request)

    @AuthUtil.restrict_access()
    async def get_by_id(self, request: Request, group_id: int) -> GroupResponse:
        return await super().get_by_id(request, group_id)

    @AuthUtil.restrict_access()
    async def create(self, data: GroupCreate, request: Request) -> GroupResponse:
        return await super().create(data, request)

    @AuthUtil.restrict_access()
    async def update(
        self, data: GroupCreate, request: Request, group_id: int
    ) -> GroupResponse:
        return await super().update(data, request, group_id)

    @AuthUtil.restrict_access()
    async def delete(self, request: Request, group_id: int) -> Response:
        return await super().delete(request, group_id)
