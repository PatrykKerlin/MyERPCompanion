from dataclasses import dataclass, field
from typing import Any

from utils.enums import View


@dataclass
class RequestData:
    sort_by: str = "id"
    order: str = "asc"
    page: int = 1
    page_size: int = 10
    has_next: bool = False
    has_prev: bool = False
    total: int = 0
    selected_inputs: set[str] = field(default_factory=set)
    input_values: dict[str, Any] = field(default_factory=dict)
    undo_stack: list[tuple[str, Any, Any]] = field(default_factory=list)
    redo_stack: list[tuple[str, Any, Any]] = field(default_factory=list)
    caller_view_key: View | None = None
    caller_data: dict[str, Any] | None = None
    is_saving: bool = False
