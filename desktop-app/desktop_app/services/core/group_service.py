from __future__ import annotations
from typing import TYPE_CHECKING

from services.base import BaseService
from schemas.core import GroupInputSchema

if TYPE_CHECKING:
    from config.context import Context


class GroupService(BaseService):
    def __init__(self, context: Context) -> None:
        super().__init__(context)

    async def get_all_groups(self, filters: dict[str, str] = {}) -> list[GroupInputSchema]:
        params = {
            "page": 1,
            "page_size": 100,
            "sort_by": "id",
            "order": "asc",
            **filters,
        }
        response = await self._get("/groups", params=params)
        return [GroupInputSchema(**item) for item in response.json()["items"]]
