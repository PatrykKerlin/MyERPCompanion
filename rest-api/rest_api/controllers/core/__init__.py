from models.core import View, Group, Module
from schemas.core import (
    ViewStrictSchema,
    ViewPlainSchema,
    GroupStrictSchema,
    GroupPlainSchema,
    ModuleStrictSchema,
    ModulePlainSchema,
)
from services.core import EndpointService, GroupService, ModuleService
from utils.factories import ControllerFactory

from .auth_controller import AuthController
from .current_user_controller import CurrentUserController
from .health_check_controller import HealthCheckController
from .translation_controller import TranslationController
from .user_controller import UserController


GroupController = ControllerFactory.create(
    model_cls=Group,
    service_cls=GroupService,
    input_schema_cls=GroupStrictSchema,
    output_schema_cls=GroupPlainSchema,
)
ModuleController = ControllerFactory.create(
    model_cls=Module,
    service_cls=ModuleService,
    input_schema_cls=ModuleStrictSchema,
    output_schema_cls=ModulePlainSchema,
)
ViewController = ControllerFactory.create(
    model_cls=View,
    service_cls=EndpointService,
    input_schema_cls=ViewStrictSchema,
    output_schema_cls=ViewPlainSchema,
)


__all__ = [
    "AuthController",
    "CurrentUserController",
    "GroupController",
    "HealthCheckController",
    "ModuleController",
    "TranslationController",
    "UserController",
    "ViewController",
]
