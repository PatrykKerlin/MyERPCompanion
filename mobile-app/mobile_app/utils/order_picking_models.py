from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderPickingItemRow:
    item_id: int
    item_index: str
    item_name: str
    to_process: int


@dataclass(frozen=True)
class OrderPickedItemRow:
    item_id: int
    item_index: str
    item_name: str
    bin_location: str
    quantity: int


@dataclass(frozen=True)
class OrderPickingBinOption:
    bin_item_id: int
    bin_id: int
    location: str
    available_quantity: int
    bin_item_quantity: int
