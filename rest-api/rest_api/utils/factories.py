from types import new_class
from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema, BaseResponseSchema
from services.base import BaseService


class RepositoryFactory:
    @classmethod
    def create(cls, entity_cls: type[BaseEntity]) -> type[BaseRepository[BaseEntity]]:
        return new_class(
            f"{entity_cls.__name__}Repository",
            [BaseRepository[entity_cls]],
            exec_body=lambda ns: ns.update({"_model_cls": entity_cls}),
        )


class ServiceFactory:
    @classmethod
    def create(
        cls,
        entity_cls: type[BaseEntity],
        repository_cls: type[BaseRepository[BaseEntity]],
        create_schema_cls: type[BaseCreateSchema],
        response_schema_cls: type[BaseResponseSchema],
    ) -> type[
        BaseService[
            BaseEntity, BaseRepository[BaseEntity], BaseCreateSchema, BaseResponseSchema
        ]
    ]:
        return new_class(
            f"{entity_cls.__name__}Service",
            [
                BaseService[
                    entity_cls, repository_cls, create_schema_cls, response_schema_cls
                ]
            ],
            exec_body=lambda ns: ns.update(
                {
                    "_repository_cls": repository_cls,
                    "_entity_cls": entity_cls,
                    "_response_schema_cls": response_schema_cls,
                }
            ),
        )
