from models.core import Endpoint, Group, Module, Setting, SettingKey
from schemas.core import (
    EndpointInputSchema,
    EndpointOutputSchema,
    GroupInputSchema,
    GroupOutputSchema,
    ModuleInputSchema,
    ModuleOutputSchema,
    SettingInputSchema,
    SettingKeyInputSchema,
    SettingKeyOutputSchema,
    SettingOutputSchema,
)
from services.core import EndpointService, GroupService, ModuleService, SettingKeyService, SettingService
from utils.factories import ControllerFactory

from .auth_controller import AuthController
from .health_check_controller import HealthCheckController
from .user_controller import UserController
from .text_controller import TextController

EndpointController = ControllerFactory.create(
    model_cls=Endpoint,
    service_cls=EndpointService,
    input_schema_cls=EndpointInputSchema,
    output_schema_cls=EndpointOutputSchema,
)
GroupController = ControllerFactory.create(
    model_cls=Group,
    service_cls=GroupService,
    input_schema_cls=GroupInputSchema,
    output_schema_cls=GroupOutputSchema,
)
ModuleController = ControllerFactory.create(
    model_cls=Module,
    service_cls=ModuleService,
    input_schema_cls=ModuleInputSchema,
    output_schema_cls=ModuleOutputSchema,
)
SettingKeyController = ControllerFactory.create(
    model_cls=SettingKey,
    service_cls=SettingKeyService,
    input_schema_cls=SettingKeyInputSchema,
    output_schema_cls=SettingKeyOutputSchema,
)
SettingController = ControllerFactory.create(
    model_cls=Setting,
    service_cls=SettingService,
    input_schema_cls=SettingInputSchema,
    output_schema_cls=SettingOutputSchema,
)

__all__ = [
    "AuthController",
    "EndpointController",
    "GroupController",
    "HealthCheckController",
    "ModuleController",
    "SettingController",
    "SettingKeyController",
    "TextController",
    "UserController",
]
