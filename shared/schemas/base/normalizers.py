from typing import Any


class Normalizers:
    @staticmethod
    def normalize_related_ids(values: Any, field_name: str = "items") -> list[int]:
        if not values:
            return []

        if not isinstance(values, list):
            raise ValueError(f"{field_name} must be a list")

        if all(isinstance(value, int) for value in values):
            return values

        try:
            return [getattr(value, "id") for value in values]
        except AttributeError as e:
            raise ValueError(f"all elements in {field_name} must be integers or objects with an 'id' attribute") from e
