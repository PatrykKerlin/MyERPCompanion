from models.core import Group, Language, Module, Theme, View
from schemas.core import (
    GroupPlainSchema,
    GroupStrictSchema,
    LanguagePlainSchema,
    LanguageStrictSchema,
    ModulePlainSchema,
    ModuleStrictSchema,
    ThemePlainSchema,
    ThemeStrictSchema,
    ViewPlainSchema,
    ViewStrictSchema,
)
from services.core import GroupService, LanguageService, ModuleService, ThemeService, ViewService
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
LanguageController = ControllerFactory.create(
    model_cls=Language,
    service_cls=LanguageService,
    input_schema_cls=LanguageStrictSchema,
    output_schema_cls=LanguagePlainSchema,
)
ModuleController = ControllerFactory.create(
    model_cls=Module,
    service_cls=ModuleService,
    input_schema_cls=ModuleStrictSchema,
    output_schema_cls=ModulePlainSchema,
)
ThemeController = ControllerFactory.create(
    model_cls=Theme,
    service_cls=ThemeService,
    input_schema_cls=ThemeStrictSchema,
    output_schema_cls=ThemePlainSchema,
)
ViewController = ControllerFactory.create(
    model_cls=View,
    service_cls=ViewService,
    input_schema_cls=ViewStrictSchema,
    output_schema_cls=ViewPlainSchema,
)


__all__ = [
    "AuthController",
    "CurrentUserController",
    "GroupController",
    "HealthCheckController",
    "LanguageController",
    "ModuleController",
    "ThemeController",
    "TranslationController",
    "UserController",
    "ViewController",
]
