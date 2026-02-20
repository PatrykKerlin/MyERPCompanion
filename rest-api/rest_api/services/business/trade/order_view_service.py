from collections.abc import Sequence

from models.base.base_model import BaseModel
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.order import Order
from repositories.base.base_repository import BaseRepository
from repositories.business.trade.order_view_repository import OrderViewRepository
from repositories.mixins.item_quantity_mixin import ItemQuantityMixin
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.business.trade.order_schema import OrderPlainSchema
from schemas.business.trade.order_view_schema import (
    OrderViewCategorySchema,
    OrderViewCustomerSchema,
    OrderViewDeliveryMethodSchema,
    OrderViewDiscountSchema,
    OrderViewExchangeRateSchema,
    OrderViewImageSchema,
    OrderViewLookupSchema,
    OrderViewResponseSchema,
    OrderViewSourceItemSchema,
    OrderViewStatusHistorySchema,
    OrderViewSupplierSchema,
    OrderViewTargetItemSchema,
)
from services.base.base_service import BaseService
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


class OrderViewService(
    BaseService[BaseModel, BaseRepository[BaseModel], BaseStrictSchema, BasePlainSchema], ItemQuantityMixin
):
    _model_cls = Order

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
            if order is None:
                raise NoResultFound(f"Order with ID {order_id} not found.")

        source_items: Sequence[Item] = []
        order_items: Sequence[AssocOrderItem] = []
        order_statuses: Sequence[AssocOrderStatus] = []

        if order:
            order_items = order.order_items
            order_statuses = order.order_statuses
            if not is_sales and order.supplier_id:
                source_items = await OrderViewRepository.get_items_for_supplier(session, order.supplier_id)
            elif is_sales and order.customer_id:
                source_items = await OrderViewRepository.get_all_items(session)
        else:
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
                            min_value=assoc.discount.min_value,
                            min_quantity=assoc.discount.min_quantity,
                            currency_id=assoc.discount.currency_id,
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
            source_items=self.__build_source_items(source_items, reserved_by_id, outbound_by_id),
            target_items=self.__build_target_items(order_items),
            status_history=self.__build_status_history(order_statuses),
            categories=[
                OrderViewCategorySchema(
                    id=row.id,
                    label=row.name,
                    discounts=[
                        OrderViewDiscountSchema(
                            id=assoc.discount.id,
                            code=assoc.discount.code,
                            percent=assoc.discount.percent,
                            min_value=assoc.discount.min_value,
                            min_quantity=assoc.discount.min_quantity,
                            currency_id=assoc.discount.currency_id,
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
    def __build_source_items(
        items: Sequence[Item], reserved_by_id: dict[int, int], outbound_by_id: dict[int, int]
    ) -> list[OrderViewSourceItemSchema]:
        return [
            OrderViewSourceItemSchema(
                id=item.id,
                index=item.index,
                name=item.name,
                ean=item.ean,
                description=item.description,
                purchase_price=item.purchase_price,
                margin=item.margin,
                vat_rate=item.vat_rate,
                is_fragile=item.is_fragile,
                category_id=item.category_id,
                category_name=item.category_name,
                width=item.width,
                height=item.height,
                length=item.length,
                weight=item.weight,
                expiration_date=item.expiration_date,
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
                        min_value=assoc.discount.min_value,
                        min_quantity=assoc.discount.min_quantity,
                        currency_id=assoc.discount.currency_id,
                    )
                    for assoc in item.item_discounts
                    if assoc.discount and assoc.discount.is_active
                ],
                images=[
                    OrderViewImageSchema(
                        url=image.url,
                        is_primary=image.is_primary,
                        order=image.order,
                        description=image.description,
                        item_id=image.item_id,
                    )
                    for image in sorted(item.images or [], key=lambda image: image.order)
                    if image.is_active
                ],
            )
            for item in items
        ]

    @staticmethod
    def __build_target_items(items: Sequence[AssocOrderItem]) -> list[OrderViewTargetItemSchema]:
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
                    margin=item.margin,
                    vat_rate=item.vat_rate,
                    width=item.width,
                    height=item.height,
                    length=item.length,
                    weight=item.weight,
                    category_id=item.category_id,
                    supplier_currency_id=item.supplier.currency_id if item.supplier else None,
                    bin_id=assoc.bin_id,
                    category_discount_id=assoc.category_discount_id,
                    customer_discount_id=assoc.customer_discount_id,
                    item_discount_id=assoc.item_discount_id,
                )
            )
        return results

    @staticmethod
    def __build_status_history(items: Sequence[AssocOrderStatus]) -> list[OrderViewStatusHistorySchema]:
        sorted_items = sorted(items, key=lambda row: row.created_at)
        return [
            OrderViewStatusHistorySchema(
                status_id=row.status_id,
                key=row.status.key if row.status else str(row.status_id),
                created_at=row.created_at,
            )
            for row in sorted_items
        ]
