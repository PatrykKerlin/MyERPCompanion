from typing import Any
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class DepartmentService(BaseService):

    async def get_all(
        self,
        _: int | None = None,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> PaginatedResponseSchema[DepartmentPlainSchema]:
        endpoint = Endpoint.DEPARTMENTS
        response = await self._get(endpoint=endpoint, query_params=query_params, token=token, view_key=view_key)
        data = response.json()
        return PaginatedResponseSchema[DepartmentPlainSchema](
            items=[DepartmentPlainSchema(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 10),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    async def get_one(
        self,
        path_param: int | None = None,
        _: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> DepartmentPlainSchema:
        endpoint = f"{Endpoint.DEPARTMENTS}/{path_param}"
        response = await self._get(endpoint=endpoint, token=token, view_key=view_key)
        data = response.json()
        return DepartmentPlainSchema(**data)

    async def create(
        self,
        _: int | None = None,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> DepartmentPlainSchema:
        endpoint = Endpoint.DEPARTMENTS
        response = await self._post(endpoint=endpoint, body_params=body_params, token=token, view_key=view_key)
        data = response.json()
        return DepartmentPlainSchema(**data)

    async def update(
        self,
        path_param: int | None = None,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> DepartmentPlainSchema:
        endpoint = f"{Endpoint.DEPARTMENTS}/{path_param}"
        response = await self._put(endpoint=endpoint, body_params=body_params, token=token, view_key=view_key)
        data = response.json()
        return DepartmentPlainSchema(**data)

    async def delete(
        self,
        path_param: int | None = None,
        _: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> bool:
        endpoint = f"{Endpoint.DEPARTMENTS}/{path_param}"
        await self._delete(endpoint=endpoint, token=token, view_key=view_key)
        return True
