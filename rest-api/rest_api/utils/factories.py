from types import new_class
from typing import TYPE_CHECKING, Any, TypeVar

from config import Context

if TYPE_CHECKING:
    from ..controllers.base import BaseController
    from ..entities.base import BaseEntity
    from ..repositories.base import BaseRepository
    from ..schemas.base import BaseInputSchema, BaseOutputSchema
    from ..services.base import BaseService


TEntity = TypeVar("TEntity", bound="BaseEntity")
TInputSchema = TypeVar("TInputSchema", bound="BaseInputSchema")
TOutputSchema = TypeVar("TOutputSchema", bound="BaseOutputSchema")
TRepository = TypeVar("TRepository", bound="BaseRepository")
TService = TypeVar("TService", bound="BaseService")
TController = TypeVar("TController", bound="BaseController")


class RepositoryFactory:
    @classmethod
    def create(cls, entity_cls: type[TEntity]) -> type["BaseRepository[TEntity]"]:
        from repositories.base import BaseRepository

        return new_class(
            f"{entity_cls.__name__}Repository",
            [BaseRepository[entity_cls]],
            exec_body=lambda namespace: namespace.update({"_entity_cls": entity_cls}),
        )


class ServiceFactory:
    @classmethod
    def create(
        cls,
        entity_cls: type[TEntity],
        repository_cls: type[TRepository],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
    ) -> type["BaseService[TEntity, TRepository, TInputSchema, TOutputSchema]"]:
        from services.base import BaseService

        return new_class(
            f"{entity_cls.__name__}Service",
            [BaseService[entity_cls, repository_cls, input_schema_cls, output_schema_cls]],
            exec_body=lambda namespace: namespace.update(
                {
                    "_repository_cls": repository_cls,
                    "_entity_cls": entity_cls,
                    "_output_schema_cls": output_schema_cls,
                }
            ),
        )


class ControllerFactory:
    @classmethod
    def create(
        cls,
        entity_cls: type[TEntity],
        service_cls: type[TService],
        input_schema_cls: type[TInputSchema],
        output_schema_cls: type[TOutputSchema],
        path: str = "",
        include: list[str] | None = None,
    ) -> type["BaseController[TService, TInputSchema, TOutputSchema]"]:
        from controllers.base import BaseController

        def exec_body(namespace: dict[str, Any]) -> None:
            def __init__(self, context: Context) -> None:
                BaseController.__init__(self, context)
                self._register_routes(
                    output_schema=output_schema_cls,
                    include=selected_methods,
                    path=path,
                )

            namespace["_service_cls"] = service_cls
            namespace["__init__"] = __init__

        method_map = {
            "get_all": BaseController.get_all,
            "get_by_id": BaseController.get_by_id,
            "create": BaseController.create,
            "update": BaseController.update,
            "delete": BaseController.delete,
        }

        allowed_methods = method_map.keys()
        selected_methods = include or list(allowed_methods)

        invalid = [method for method in selected_methods if method not in allowed_methods]
        if invalid:
            raise ValueError(f"Invalid method(s): {invalid}. Allowed: {list(allowed_methods)}")

        return new_class(
            f"{entity_cls.__name__}Controller",
            [BaseController[service_cls, input_schema_cls, output_schema_cls]],
            exec_body=exec_body,
        )
