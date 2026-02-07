from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError

from config.context import Context
from controllers.base.base_controller import BaseController
from schemas.business.reporting.sales_report_schema import SalesReportFilterSchema, SalesReportResponseSchema
from services.business.reporting.sales_report_service import SalesReportService
from utils.auth import Auth
from utils.enums import Permission


class SalesReportController:
    def __init__(self, context: Context, auth: Auth) -> None:
        self._logger = context.logger
        self._service = SalesReportService()
        self.router = APIRouter()
        dependencies = [Depends(auth.restrict_access(permissions=[Permission.CAN_READ], controller=self.__class__.__name__))]
        self.router.add_api_route(
            path="",
            endpoint=self.get_sales_report,
            methods=["GET"],
            response_model=SalesReportResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=dependencies,
        )

    async def get_sales_report(
        self,
        request: Request,
        filters: Annotated[SalesReportFilterSchema, Depends()],
    ) -> SalesReportResponseSchema:
        try:
            session = BaseController._get_request_session(request)
            items, totals = await self._service.get_report(
                session=session,
                filters=filters,
            )
            return SalesReportResponseSchema(
                items=items,
                totals=totals,
            )
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_sales_report.__qualname__}")
            raise
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_sales_report.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
