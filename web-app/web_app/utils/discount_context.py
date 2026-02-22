from dataclasses import dataclass


@dataclass(frozen=True)
class DiscountContext:
    quantities: dict[int, int]
    base_net_map: dict[int, float]
    order_quantity: int
    order_net: float
    category_quantities: dict[int, int]
    category_net_map: dict[int, float]
