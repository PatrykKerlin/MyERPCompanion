from __future__ import annotations

from decimal import Decimal

from repositories.business.reporting.sales_forecast_report_repository import SalesForecastReportRepository
from schemas.business.reporting.sales_forecast_report_schema import (
    SalesForecastReportFilterSchema,
    SalesForecastReportRowSchema,
    SalesForecastReportTotalsSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession


class SalesForecastReportService:
    async def get_report(
        self,
        session: AsyncSession,
        filters: SalesForecastReportFilterSchema,
    ) -> tuple[list[SalesForecastReportRowSchema], SalesForecastReportTotalsSchema]:
        latest_run = await SalesForecastReportRepository.get_latest_successful_run(session)
        if latest_run is None:
            return [], SalesForecastReportTotalsSchema()

        latest_run_id, latest_run_finished_at = latest_run
        rows_result = await SalesForecastReportRepository.get_rows(
            session=session,
            run_id=latest_run_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            item_id=filters.item_id,
            customer_id=filters.customer_id,
            category_id=filters.category_id,
            currency_id=filters.currency_id,
            discount_from=filters.discount_from,
            discount_to=filters.discount_to,
        )
        totals_row = await SalesForecastReportRepository.get_totals(
            session=session,
            run_id=latest_run_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            item_id=filters.item_id,
            customer_id=filters.customer_id,
            category_id=filters.category_id,
            currency_id=filters.currency_id,
            discount_from=filters.discount_from,
            discount_to=filters.discount_to,
        )
        discount_steps = await SalesForecastReportRepository.get_discount_steps(
            session=session,
            run_id=latest_run_id,
        )

        rows = [
            SalesForecastReportRowSchema(
                result_id=row.result_id,
                run_id=row.run_id,
                predicted_at=row.predicted_at,
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                item_id=row.item_id,
                item_name=row.item_name,
                category_id=row.category_id,
                category_name=row.category_name,
                currency_id=row.currency_id,
                currency_code=row.currency_code,
                predicted_net=SalesForecastReportService.__to_float(row.predicted_net),
                predicted_gross=SalesForecastReportService.__to_float(row.predicted_gross),
                discount_rate_assumption=SalesForecastReportService.__to_float(row.discount_rate_assumption),
                horizon_months=int(row.horizon_months or 0),
            )
            for row in rows_result
        ]
        totals = SalesForecastReportTotalsSchema(
            rows_count=int(totals_row["rows_count"] or 0),
            periods_count=int(totals_row["periods_count"] or 0),
            total_predicted_net=SalesForecastReportService.__to_float(totals_row["total_predicted_net"]),
            total_predicted_gross=SalesForecastReportService.__to_float(totals_row["total_predicted_gross"]),
            discount_steps=discount_steps,
            latest_run_id=latest_run_id,
            latest_run_finished_at=latest_run_finished_at,
        )
        return rows, totals

    @staticmethod
    def __to_float(value: Decimal | float | int | None) -> float:
        if value is None:
            return 0
        return float(value)
