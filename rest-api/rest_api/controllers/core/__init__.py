from models.core import Endpoint, Group, Module
from schemas.core import (
    EndpointInputSchema,
    EndpointOutputSchema,
    GroupInputSchema,
    GroupOutputSchema,
    ModuleInputSchema,
    ModuleOutputSchema,
)
from services.core import EndpointService, GroupService, ModuleService
from utils.factories import ControllerFactory

from .auth_controller import AuthController
from .current_user_controller import CurrentUserController
from .health_check_controller import HealthCheckController
from .text_controller import TextController
from .user_controller import UserController

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


__all__ = [
    "AuthController",
    "CurrentUserController",
    "EndpointController",
    "GroupController",
    "HealthCheckController",
    "ModuleController",
    "TextController",
    "UserController",
]
