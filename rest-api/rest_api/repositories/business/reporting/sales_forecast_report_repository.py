from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from models.ai.ai_task_run import AiTaskRun
from models.ai.sales_forecast import SalesForecast
from models.business.logistic.category import Category
from models.business.logistic.item import Item
from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from sqlalchemy import DateTime, Select, case, cast, desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement


class SalesForecastReportRepository:
    _task_key = "sales_forecast"
    _aggregation_net = "month_net"
    _aggregation_quantity = "month_quantity"

    @staticmethod
    async def get_latest_successful_run(session: AsyncSession) -> tuple[int, datetime | None] | None:
        query = (
            select(
                AiTaskRun.id.label("run_id"),
                cast(AiTaskRun.finished_at, DateTime(timezone=True)).label("finished_at"),
            )
            .where(
                AiTaskRun.task_key == SalesForecastReportRepository._task_key,
                AiTaskRun.status == "success",
            )
            .order_by(desc(AiTaskRun.id))
            .limit(1)
        )
        result = await session.execute(query)
        row = result.one_or_none()
        if row is None:
            return None
        return int(row.run_id), row.finished_at

    @staticmethod
    async def get_rows(
        session: AsyncSession,
        run_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
        item_id: int | None = None,
        customer_id: int | None = None,
        category_id: int | None = None,
        currency_id: int | None = None,
        discount_from: float | None = None,
        discount_to: float | None = None,
    ) -> list[Any]:
        query = SalesForecastReportRepository.__build_rows_query(
            run_id=run_id,
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
            discount_from=discount_from,
            discount_to=discount_to,
        )
        result = await session.execute(query)
        return list(result)

    @staticmethod
    async def get_totals(
        session: AsyncSession,
        run_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
        item_id: int | None = None,
        customer_id: int | None = None,
        category_id: int | None = None,
        currency_id: int | None = None,
        discount_from: float | None = None,
        discount_to: float | None = None,
    ) -> dict[str, Decimal | int | None]:
        query = SalesForecastReportRepository.__build_totals_query(
            run_id=run_id,
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
            discount_from=discount_from,
            discount_to=discount_to,
        )
        result = await session.execute(query)
        row = result.one()
        return {
            "rows_count": row.rows_count,
            "periods_count": row.periods_count,
            "total_predicted_net": row.total_predicted_net,
            "total_predicted_quantity": row.total_predicted_quantity,
        }

    @staticmethod
    async def get_discount_steps(session: AsyncSession, run_id: int) -> list[float]:
        query = (
            select(distinct(SalesForecast.discount_rate_assumption))
            .where(
                SalesForecast.run_id == run_id,
                SalesForecast.aggregation == SalesForecastReportRepository._aggregation_net,
                SalesForecast.discount_rate_assumption.is_not(None),
            )
            .order_by(SalesForecast.discount_rate_assumption)
        )
        result = await session.execute(query)
        return [float(row[0]) for row in result if row[0] is not None]

    @staticmethod
    def __build_rows_query(
        run_id: int,
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
        discount_from: float | None,
        discount_to: float | None,
    ) -> Select:
        where_clause = SalesForecastReportRepository.__build_filters(
            run_id=run_id,
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
            discount_from=discount_from,
            discount_to=discount_to,
        )
        predicted_net = func.coalesce(
            func.sum(
                case(
                    (
                        SalesForecast.aggregation == SalesForecastReportRepository._aggregation_net,
                        SalesForecast.predicted_quantity,
                    ),
                    else_=0,
                )
            ),
            0,
        ).label("predicted_net")
        predicted_quantity = func.coalesce(
            func.sum(
                case(
                    (
                        SalesForecast.aggregation.in_(
                            [
                                SalesForecastReportRepository._aggregation_quantity,
                            ]
                        ),
                        SalesForecast.predicted_quantity,
                    ),
                    else_=0,
                )
            ),
            0,
        ).label("predicted_quantity")
        return (
            select(
                func.min(SalesForecast.id).label("result_id"),
                SalesForecast.run_id.label("run_id"),
                SalesForecast.predicted_at.label("predicted_at"),
                Customer.id.label("customer_id"),
                Customer.company_name.label("customer_name"),
                Item.id.label("item_id"),
                Item.name.label("item_name"),
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                SalesForecast.currency_id.label("currency_id"),
                Currency.code.label("currency_code"),
                predicted_net,
                predicted_quantity,
                SalesForecast.discount_rate_assumption.label("discount_rate_assumption"),
                SalesForecast.horizon_months.label("horizon_months"),
            )
            .select_from(SalesForecast)
            .join(Item, SalesForecast.item_id == Item.id)
            .join(Category, SalesForecast.category_id == Category.id)
            .join(Customer, SalesForecast.customer_id == Customer.id)
            .join(Currency, SalesForecast.currency_id == Currency.id)
            .where(*where_clause)
            .group_by(
                SalesForecast.run_id,
                SalesForecast.predicted_at,
                Customer.id,
                Customer.company_name,
                Item.id,
                Item.name,
                Category.id,
                Category.name,
                SalesForecast.currency_id,
                Currency.code,
                SalesForecast.discount_rate_assumption,
                SalesForecast.horizon_months,
            )
            .order_by(SalesForecast.predicted_at, Customer.id, Item.id, Category.id, SalesForecast.currency_id)
        )

    @staticmethod
    def __build_totals_query(
        run_id: int,
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
        discount_from: float | None,
        discount_to: float | None,
    ) -> Select:
        where_clause = SalesForecastReportRepository.__build_filters(
            run_id=run_id,
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
            discount_from=discount_from,
            discount_to=discount_to,
        )
        return (
            select(
                func.count(SalesForecast.id)
                .filter(SalesForecast.aggregation == SalesForecastReportRepository._aggregation_net)
                .label("rows_count"),
                func.count(distinct(SalesForecast.predicted_at))
                .filter(SalesForecast.aggregation == SalesForecastReportRepository._aggregation_net)
                .label("periods_count"),
                func.coalesce(
                    func.sum(SalesForecast.predicted_quantity).filter(
                        SalesForecast.aggregation == SalesForecastReportRepository._aggregation_net
                    ),
                    0,
                ).label("total_predicted_net"),
                func.coalesce(
                    func.sum(SalesForecast.predicted_quantity).filter(
                        SalesForecast.aggregation.in_(
                            [
                                SalesForecastReportRepository._aggregation_quantity,
                            ]
                        )
                    ),
                    0,
                ).label("total_predicted_quantity"),
            )
            .select_from(SalesForecast)
            .join(Item, SalesForecast.item_id == Item.id)
            .join(Category, SalesForecast.category_id == Category.id)
            .join(Customer, SalesForecast.customer_id == Customer.id)
            .join(Currency, SalesForecast.currency_id == Currency.id)
            .where(*where_clause)
        )

    @staticmethod
    def __build_filters(
        run_id: int,
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
        discount_from: float | None,
        discount_to: float | None,
    ) -> list[ColumnElement[bool]]:
        where_clause = [
            SalesForecast.run_id == run_id,
            SalesForecast.aggregation.in_(
                [
                    SalesForecastReportRepository._aggregation_net,
                    SalesForecastReportRepository._aggregation_quantity,
                ]
            ),
            SalesForecast.currency_id.is_not(None),
            SalesForecast.predicted_quantity.is_not(None),
            SalesForecast.horizon_months.is_not(None),
            SalesForecast.discount_rate_assumption.is_not(None),
            Item.is_active.is_(True),
            Category.is_active.is_(True),
            Customer.is_active.is_(True),
            Currency.is_active.is_(True),
        ]
        if date_from is not None:
            where_clause.append(SalesForecast.predicted_at >= date_from)
        if date_to is not None:
            where_clause.append(SalesForecast.predicted_at <= date_to)
        if customer_id is not None:
            where_clause.append(SalesForecast.customer_id == customer_id)
        if item_id is not None:
            where_clause.append(SalesForecast.item_id == item_id)
        if category_id is not None:
            where_clause.append(SalesForecast.category_id == category_id)
        if currency_id is not None:
            where_clause.append(SalesForecast.currency_id == currency_id)
        if discount_from is not None:
            where_clause.append(SalesForecast.discount_rate_assumption >= discount_from)
        if discount_to is not None:
            where_clause.append(SalesForecast.discount_rate_assumption <= discount_to)
        return where_clause
