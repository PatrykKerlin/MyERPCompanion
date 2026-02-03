from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.order import Order
from repositories.business.trade.order_view_repository import OrderViewRepository
from repositories.mixins.item_quantity_mixin import ItemQuantityMixin
from schemas.business.trade.order_schema import OrderPlainSchema
from schemas.business.trade.order_view_schema import (
    OrderViewDeliveryMethodSchema,
    OrderViewDiscountSchema,
    OrderViewExchangeRateSchema,
    OrderViewCustomerSchema,
    OrderViewCategorySchema,
    OrderViewLookupSchema,
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewSupplierSchema,
    OrderViewTargetItemSchema,
)


class OrderViewService(ItemQuantityMixin):
    async def get_view(
        self, session: AsyncSession, is_sales: bool, order_id: int | None = None
    ) -> OrderViewResponseSchema:
        (
            suppliers,
            customers,
            currencies,
            delivery_methods,
            statuses,
            categories,
            exchange_rates,
        ) = await OrderViewRepository.get_lookups(session)

        order: Order | None = None
        if order_id is not None:
            order = await OrderViewRepository.get_order_with_relations(session, order_id, is_sales)

        source_items: Sequence[Item] = []
        order_items: Sequence[AssocOrderItem] = []
        order_statuses: Sequence[AssocOrderStatus] = []

        if order:
            order_items = order.order_items
            order_statuses = order.order_statuses
            if not is_sales and order.supplier_id:
                source_items = await OrderViewRepository.get_items_for_supplier(session, order.supplier_id)
            elif is_sales:
                source_items = await OrderViewRepository.get_all_items(session)

        reserved_by_id = await self._get_reserved_quantities(session, source_items)
        outbound_by_id = await self._get_outbound_quantities(session, source_items)

        response = OrderViewResponseSchema(
            order=OrderPlainSchema.model_validate(order) if order else None,
            suppliers=[
                OrderViewSupplierSchema(id=row.id, label=row.company_name, currency_id=row.currency_id)
                for row in suppliers
            ],
            customers=[
                OrderViewCustomerSchema(
                    id=row.id,
                    label=row.company_name,
                    discounts=[
                        OrderViewDiscountSchema(
                            id=assoc.discount.id,
                            code=assoc.discount.code,
                            percent=assoc.discount.percent,
                        )
                        for assoc in row.customer_discounts
                        if assoc.discount and assoc.discount.is_active
                    ],
                )
                for row in customers
            ],
            currencies=[OrderViewLookupSchema(id=row.id, label=row.code, status_number=None) for row in currencies],
            delivery_methods=[
                OrderViewDeliveryMethodSchema(
                    id=row.id,
                    label=row.name,
                    price_per_unit=row.price_per_unit,
                    max_width=row.max_width,
                    max_height=row.max_height,
                    max_length=row.max_length,
                    max_weight=row.max_weight,
                    carrier_currency_id=row.carrier.currency_id if row.carrier else None,
                )
                for row in delivery_methods
            ],
            statuses=[OrderViewLookupSchema(id=row.id, label=row.key, status_number=row.order) for row in statuses],
            source_items=self._build_source_items(source_items, reserved_by_id, outbound_by_id),
            target_items=self._build_target_items(order_items),
            status_history=self._build_status_history(order_statuses),
            categories=[
                OrderViewCategorySchema(
                    id=row.id,
                    label=row.name,
                    discounts=[
                        OrderViewDiscountSchema(
                            id=assoc.discount.id,
                            code=assoc.discount.code,
                            percent=assoc.discount.percent,
                        )
                        for assoc in row.category_discounts
                        if assoc.discount and assoc.discount.is_active
                    ],
                )
                for row in categories
            ],
            exchange_rates=(
                [
                    OrderViewExchangeRateSchema(
                        rate=row.rate,
                        base_currency_id=row.base_currency_id,
                        quote_currency_id=row.quote_currency_id,
                    )
                    for row in exchange_rates
                ]
                if exchange_rates
                else None
            ),
        )
        return response

    @staticmethod
    def _build_source_items(
        items: Sequence[Item], reserved_by_id: dict[int, int], outbound_by_id: dict[int, int]
    ) -> list[OrderViewSourceItemSchema]:
        return [
            OrderViewSourceItemSchema(
                id=item.id,
                index=item.index,
                name=item.name,
                ean=item.ean,
                purchase_price=item.purchase_price,
                vat_rate=item.vat_rate,
                category_id=item.category_id,
                width=item.width,
                height=item.height,
                length=item.length,
                weight=item.weight,
                stock_quantity=item.stock_quantity,
                reserved_quantity=reserved_by_id.get(item.id, 0),
                outbound_quantity=outbound_by_id.get(item.id, 0),
                moq=item.moq,
                is_package=item.is_package,
                supplier_currency_id=item.supplier.currency_id if item.supplier else None,
                discounts=[
                    OrderViewDiscountSchema(
                        id=assoc.discount.id,
                        code=assoc.discount.code,
                        percent=assoc.discount.percent,
                    )
                    for assoc in item.item_discounts
                    if assoc.discount and assoc.discount.is_active
                ],
            )
            for item in items
        ]

    @staticmethod
    def _build_target_items(items: Sequence[AssocOrderItem]) -> list[OrderViewTargetItemSchema]:
        results: list[OrderViewTargetItemSchema] = []
        for assoc in items:
            item = assoc.item
            results.append(
                OrderViewTargetItemSchema(
                    id=assoc.id,
                    item_id=assoc.item_id,
                    index=item.index,
                    name=item.name,
                    quantity=assoc.quantity,
                    purchase_price=item.purchase_price,
                    vat_rate=item.vat_rate,
                    width=item.width,
                    height=item.height,
                    length=item.length,
                    weight=item.weight,
                    category_id=item.category_id,
                    supplier_currency_id=item.supplier.currency_id if item.supplier else None,
                    category_discount_id=assoc.category_discount_id,
                    customer_discount_id=assoc.customer_discount_id,
                    item_discount_id=assoc.item_discount_id,
                )
            )
        return results

    @staticmethod
    def _build_status_history(items: Sequence[AssocOrderStatus]) -> list[OrderViewStatusHistorySchema]:
        sorted_items = sorted(items, key=lambda row: row.created_at)
        return [
            OrderViewStatusHistorySchema(
                status_id=row.status_id,
                key=row.status.key if row.status else str(row.status_id),
                created_at=row.created_at,
            )
            for row in sorted_items
        ]
