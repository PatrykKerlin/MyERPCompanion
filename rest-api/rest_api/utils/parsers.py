from typing import Any

from fastapi import Request

from schemas.core import FilterParams


class FilterParamsParser:
    def __call__(self, request: Request) -> FilterParams:
        parsed: dict[str, Any] = {}

        for key, value in request.query_params.items():
            if key in {"page", "page_size", "sort_by", "order"}:
                continue
            if value.lower() == "true":
                parsed[key] = True
            elif value.lower() == "false":
                parsed[key] = False
            elif value.isdigit():
                parsed[key] = int(value)
            else:
                try:
                    parsed[key] = float(value)
                except ValueError:
                    parsed[key] = value

        return FilterParams(filters=parsed)
