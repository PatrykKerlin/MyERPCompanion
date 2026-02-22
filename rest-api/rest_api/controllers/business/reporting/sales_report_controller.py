from __future__ import annotations

from typing import Annotated

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Depends, Request, status
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.business.reporting.sales_report_schema import SalesReportFilterSchema, SalesReportResponseSchema
from services.business.reporting.sales_report_service import SalesReportService
from utils.auth import Auth
from utils.enums import Permission


class SalesReportController(BaseController[SalesReportService, BaseStrictSchema, BasePlainSchema]):
    _input_schema_cls = BaseStrictSchema
    _service_cls = SalesReportService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._register_routes(output_schema=BasePlainSchema, include={})
        self.router.add_api_route(
            path="",
            endpoint=self.get_sales_report,
            methods=["GET"],
            response_model=SalesReportResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )

    @BaseController.handle_exceptions()
    async def get_sales_report(
        self,
        request: Request,
        filters: Annotated[SalesReportFilterSchema, Depends()],
    ) -> SalesReportResponseSchema:
        session = BaseController._get_request_session(request)
        items, totals, first_sales_date = await self._service.get_report(
            session=session,
            filters=filters,
        )
        return SalesReportResponseSchema(
            items=items,
            totals=totals,
            first_sales_date=first_sales_date,
        )
