from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.business.reporting.sales_report_repository import SalesReportRepository
from schemas.business.reporting.sales_report_schema import (
    SalesReportFilterSchema,
    SalesReportRowSchema,
    SalesReportTotalsSchema,
)


class SalesReportService:
    async def get_report(
        self,
        session: AsyncSession,
        filters: SalesReportFilterSchema,
    ) -> tuple[list[SalesReportRowSchema], SalesReportTotalsSchema]:
        rows_result = await SalesReportRepository.get_rows(
            session=session,
            date_from=filters.date_from,
            date_to=filters.date_to,
            item_id=filters.item_id,
            customer_id=filters.customer_id,
            category_id=filters.category_id,
            currency_id=filters.currency_id,
        )
        totals_row = await SalesReportRepository.get_totals(
            session=session,
            date_from=filters.date_from,
            date_to=filters.date_to,
            item_id=filters.item_id,
            customer_id=filters.customer_id,
            category_id=filters.category_id,
            currency_id=filters.currency_id,
        )

        rows = [
            SalesReportRowSchema(
                order_item_id=row.order_item_id,
                order_id=row.order_id,
                order_number=row.order_number,
                order_date=row.order_date,
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                item_id=row.item_id,
                item_name=row.item_name,
                category_id=row.category_id,
                category_name=row.category_name,
                quantity=row.quantity,
                total_net=SalesReportService.__to_float(row.total_net),
                total_vat=SalesReportService.__to_float(row.total_vat),
                total_gross=SalesReportService.__to_float(row.total_gross),
                total_discount=SalesReportService.__to_float(row.total_discount),
            )
            for row in rows_result
        ]
        totals = SalesReportTotalsSchema(
            orders_count=int(totals_row["orders_count"] or 0),
            rows_count=len(rows),
            quantity=int(totals_row["quantity"] or 0),
            total_net=SalesReportService.__to_float(totals_row["total_net"]),
            total_vat=SalesReportService.__to_float(totals_row["total_vat"]),
            total_gross=SalesReportService.__to_float(totals_row["total_gross"]),
            total_discount=SalesReportService.__to_float(totals_row["total_discount"]),
        )
        return rows, totals

    @staticmethod
    def __to_float(value: Decimal | float | int | None) -> float:
        if value is None:
            return 0
        return float(value)
