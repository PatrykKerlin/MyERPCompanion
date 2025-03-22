from inspect import signature
from typing import Type, TypeVar

T = TypeVar("T")


def create_or_update_instance(cls: Type[T], data: dict, instance: T | None = None) -> T:
    init_params = signature(cls.__init__).parameters
    filtered_data = {
        key: value for key, value in data.items()
        if key in init_params and not key.startswith("_")
    }

    if not instance:
        return cls(**filtered_data)

    instance.__dict__.update(filtered_data)

    return instance


def get_instance_attributes(instance: T) -> dict:
    instance_keys = set(vars(instance).keys())
    property_keys = {key for key in dir(instance.__class__) if isinstance(getattr(instance.__class__, key), property)}
    all_keys = instance_keys.union(property_keys)
    instance_attrs = {key: getattr(instance, key) for key in all_keys}

    return instance_attrs
