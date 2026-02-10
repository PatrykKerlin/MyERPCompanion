from types import new_class
from typing import TypeVar

from models.base.base_model import BaseModel
from repositories.base.base_repository import BaseRepository

TModel = TypeVar("TModel", bound=BaseModel)


class RepositoryFactory:
    @classmethod
    def create(cls, model_cls: type[TModel]) -> type[BaseRepository[TModel]]:

        return new_class(
            f"{model_cls.__name__}Repository",
            [BaseRepository[model_cls]],
            exec_body=lambda namespace: namespace.update({"_model_cls": model_cls}),
        )
