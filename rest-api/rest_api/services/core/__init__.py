from models.core import View, Group
from repositories.core import ViewRepository, GroupRepository
from schemas.core import ViewStrictSchema, ViewPlainSchema, GroupStrictSchema, GroupPlainSchema
from utils.factories import ServiceFactory

from .module_service import ModuleService
from .translation_service import TranslationService
from .user_service import UserService

EndpointService = ServiceFactory.create(
    model_cls=View,
    repository_cls=ViewRepository,
    input_schema_cls=ViewStrictSchema,
    output_schema_cls=ViewPlainSchema,
)
GroupService = ServiceFactory.create(
    model_cls=Group,
    repository_cls=GroupRepository,
    input_schema_cls=GroupStrictSchema,
    output_schema_cls=GroupPlainSchema,
)


__all__ = [
    "EndpointService",
    "GroupService",
    "ModuleService",
    "TranslationService",
    "UserService",
]
