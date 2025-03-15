from inspect import signature
from typing import Type


class BaseDTO:
    def __init__(self, id: int) -> None:
        self.id = id

    @classmethod
    def from_entity(cls: Type["BaseDTO"], entity: object) -> "BaseDTO":
        init_params = signature(cls.__init__).parameters
        entity_dict = {
            key: value
            for key, value in entity.__dict__.items()
            if key in init_params and not key.startswith("_")
        }
        return cls(**entity_dict)
