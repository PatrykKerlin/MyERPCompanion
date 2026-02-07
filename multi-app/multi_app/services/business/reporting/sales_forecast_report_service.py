from __future__ import annotations

from typing import Any

from schemas.base.base_schema import BaseStrictSchema
from schemas.business.reporting.sales_forecast_report_schema import SalesForecastReportResponseSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class SalesForecastReportService(BaseService[SalesForecastReportResponseSchema, BaseStrictSchema]):
    _plain_schema_cls = SalesForecastReportResponseSchema

    @BaseService.handle_token_refresh
    async def get_report(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: BaseStrictSchema | list[BaseStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> SalesForecastReportResponseSchema:
        response = await self._get(endpoint=str(endpoint), query_params=query_params, tokens=tokens, module_id=module_id)
        data = response.json()
        return self._plain_schema_cls(**data)
