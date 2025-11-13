from controllers.core.auth_controller import AuthController
from controllers.core.current_user_controller import CurrentUserController
from controllers.core.health_check_controller import HealthCheckController
from controllers.core.image_controller import ImageController
from controllers.core.translation_controller import TranslationController
from controllers.core.user_controller import UserController
from models.core.group import Group
from models.core.language import Language
from models.core.module import Module
from models.core.theme import Theme
from models.core.view import View
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from schemas.core.theme_schema import ThemePlainSchema, ThemeStrictSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core import GroupService, LanguageService, ThemeService
from services.core.module_service import ModuleService
from services.core import ViewService
from utils.controller_factory import ControllerFactory


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
    "ImageController",
    "LanguageController",
    "ModuleController",
    "ThemeController",
    "TranslationController",
    "UserController",
    "ViewController",
]
