from dtos.base import BaseDTO


class EndpointDTO(BaseDTO):
    controller: str
    path: str
    tag: str | None = None
    module_id: int
