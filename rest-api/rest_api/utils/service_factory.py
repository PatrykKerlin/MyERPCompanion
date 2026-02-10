from types import new_class
from typing import TypeVar

from models.base.base_model import BaseModel
from repositories.base.base_repository import BaseRepository
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from services.base.base_service import BaseService

TModel = TypeVar("TModel", bound=BaseModel)
TInputSchema = TypeVar("TInputSchema", bound=BaseStrictSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BasePlainSchema)
TRepository = TypeVar("TRepository", bound=BaseRepository)


class ServiceFactory:
    @classmethod
    def create(
        cls,
        model_cls: type[TModel],
        repository_cls: type[TRepository],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
    ) -> type[BaseService[TModel, TRepository, TInputSchema, TOutputSchema]]:

        return new_class(
            f"{model_cls.__name__}Service",
            [BaseService[model_cls, repository_cls, input_schema_cls, output_schema_cls]],
            exec_body=lambda namespace: namespace.update(
                {
                    "_repository_cls": repository_cls,
                    "_model_cls": model_cls,
                    "_output_schema_cls": output_schema_cls,
                }
            ),
        )
