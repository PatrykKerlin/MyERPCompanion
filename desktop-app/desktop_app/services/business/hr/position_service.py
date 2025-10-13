from typing import Any
from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.hr.position_schema import PositionPlainSchema
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class PositionService(BaseService):
    async def get_all_currencies(
        self,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> dict[str, int]:
        page = 1
        currencies: dict[str, int] = {}
        endpoint = Endpoint.CURRENCIES
        params = {"page": page}

        while True:
            response = await self._get(endpoint=endpoint, query_params=params, token=token, view_key=view_key)
            data = response.json()
            schemas = [CurrencyPlainSchema(**currency) for currency in data.get("items", [])]
            currencies.update({schema.code: schema.id for schema in schemas})
            if not data.get("has_next", False):
                break
            page += 1

        return currencies

    async def get_all_departments(
        self,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> dict[str, int]:
        page = 1
        departments: dict[str, int] = {}
        endpoint = Endpoint.DEPARTMENTS
        params = {"page": page}

        while True:
            response = await self._get(endpoint=endpoint, query_params=params, token=token, view_key=view_key)
            data = response.json()
            schemas = [DepartmentPlainSchema(**department) for department in data.get("items", [])]
            departments.update({schema.code: schema.id for schema in schemas})
            if not data.get("has_next", False):
                break
            page += 1

        return departments

    async def get_all(
        self,
        _: int | None = None,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> PaginatedResponseSchema[PositionPlainSchema]:
        endpoint = Endpoint.POSITIONS
        response = await self._get(endpoint=endpoint, query_params=query_params, token=token, view_key=view_key)
        data = response.json()
        return PaginatedResponseSchema[PositionPlainSchema](
            items=[PositionPlainSchema(**item) for item in data.get("items", [])],
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
    ) -> PositionPlainSchema:
        endpoint = f"{Endpoint.POSITIONS}/{path_param}"
        response = await self._get(endpoint=endpoint, token=token, view_key=view_key)
        data = response.json()
        return PositionPlainSchema(**data)

    async def create(
        self,
        _: int | None = None,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> PositionPlainSchema:
        endpoint = Endpoint.POSITIONS
        response = await self._post(endpoint=endpoint, body_params=body_params, token=token, view_key=view_key)
        data = response.json()
        return PositionPlainSchema(**data)

    async def update(
        self,
        path_param: int | None = None,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> PositionPlainSchema:
        endpoint = f"{Endpoint.POSITIONS}/{path_param}"
        response = await self._put(endpoint=endpoint, body_params=body_params, token=token, view_key=view_key)
        data = response.json()
        return PositionPlainSchema(**data)

    async def delete(
        self,
        path_param: int | None = None,
        _: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> bool:
        endpoint = f"{Endpoint.POSITIONS}/{path_param}"
        await self._delete(endpoint=endpoint, token=token, view_key=view_key)
        return True
