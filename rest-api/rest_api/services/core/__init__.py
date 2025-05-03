from models.core import Endpoint, Group, Setting, SettingKey
from repositories.core import EndpointRepository, GroupRepository, SettingKeyRepository, SettingRepository
from schemas.core import (
    EndpointInputSchema,
    EndpointOutputSchema,
    GroupInputSchema,
    GroupOutputSchema,
    SettingInputSchema,
    SettingKeyInputSchema,
    SettingKeyOutputSchema,
    SettingOutputSchema,
)
from utils.factories import ServiceFactory

from .module_service import ModuleService
from .user_service import UserService

EndpointService = ServiceFactory.create(
    model_cls=Endpoint,
    repository_cls=EndpointRepository,
    input_schema_cls=EndpointInputSchema,
    output_schema_cls=EndpointOutputSchema,
)
GroupService = ServiceFactory.create(
    model_cls=Group,
    repository_cls=GroupRepository,
    input_schema_cls=GroupInputSchema,
    output_schema_cls=GroupOutputSchema,
)
SettingKeyService = ServiceFactory.create(
    model_cls=SettingKey,
    repository_cls=SettingKeyRepository,
    input_schema_cls=SettingKeyInputSchema,
    output_schema_cls=SettingKeyOutputSchema,
)
SettingService = ServiceFactory.create(
    model_cls=Setting,
    repository_cls=SettingRepository,
    input_schema_cls=SettingInputSchema,
    output_schema_cls=SettingOutputSchema,
)

__all__ = ["EndpointService", "GroupService", "ModuleService", "SettingKeyService", "SettingService", "UserService"]
