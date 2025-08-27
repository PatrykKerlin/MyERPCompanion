from typing import Any


class Normalizers:
    @staticmethod
    def normalize_related_id_list(values: list[Any]) -> list[int]:
        if not values:
            return []

        if all(isinstance(value, int) for value in values):
            return values

        id_list: list[int] = []
        for value in values:
            if hasattr(value, "id"):
                id = getattr(value, "id")
                if isinstance(id, int):
                    id_list.append(id)

        return id_list

    @staticmethod
    def normalize_related_single_id(value: Any) -> int | None:
        if not value:
            return None

        if isinstance(value, int):
            return value

        if hasattr(value, "id"):
            id = getattr(value, "id")
            if isinstance(id, int):
                return id

        return None
