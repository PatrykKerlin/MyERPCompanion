from controllers.core.auth_controller import AuthController
from controllers.core.current_user_controller import CurrentUserController
from controllers.core.health_check_controller import HealthCheckController
from controllers.core.image_controller import ImageController
from controllers.core.translation_controller import TranslationController
from controllers.core.user_controller import UserController
from models.core.assoc_module_group import AssocModuleGroup
from models.core.assoc_user_group import AssocUserGroup
from models.core.assoc_view_controller import AssocViewController
from models.core.controller import Controller
from models.core.group import Group
from models.core.language import Language
from models.core.module import Module
from models.core.theme import Theme
from models.core.view import View
from schemas.core.assoc_module_group_schema import AssocModuleGroupPlainSchema, AssocModuleGroupStrictSchema
from schemas.core.assoc_user_group_schema import AssocUserGroupPlainSchema, AssocUserGroupStrictSchema
from schemas.core.assoc_view_controller_schema import AssocViewControllerPlainSchema, AssocViewControllerStrictSchema
from schemas.core.controller_schema import ControllerPlainSchema, ControllerStrictSchema
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from schemas.core.theme_schema import ThemePlainSchema, ThemeStrictSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core import (
    AssocModuleGroupService,
    AssocUserGroupService,
    AssocViewControllerService,
    ControllerService,
    GroupService,
    LanguageService,
    ThemeService,
    ViewService,
)
from services.core.module_service import ModuleService
from utils.controller_factory import ControllerFactory
from utils.enums import Action

GroupController = ControllerFactory.create(
    model_cls=Group,
    service_cls=GroupService,
    input_schema_cls=GroupStrictSchema,
    output_schema_cls=GroupPlainSchema,
)
AssocModuleGroupController = ControllerFactory.create(
    model_cls=AssocModuleGroup,
    service_cls=AssocModuleGroupService,
    input_schema_cls=AssocModuleGroupStrictSchema,
    output_schema_cls=AssocModuleGroupPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
AssocUserGroupController = ControllerFactory.create(
    model_cls=AssocUserGroup,
    service_cls=AssocUserGroupService,
    input_schema_cls=AssocUserGroupStrictSchema,
    output_schema_cls=AssocUserGroupPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
AssocViewControllerController = ControllerFactory.create(
    model_cls=AssocViewController,
    service_cls=AssocViewControllerService,
    input_schema_cls=AssocViewControllerStrictSchema,
    output_schema_cls=AssocViewControllerPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
ControllerController = ControllerFactory.create(
    model_cls=Controller,
    service_cls=ControllerService,
    input_schema_cls=ControllerStrictSchema,
    output_schema_cls=ControllerPlainSchema,
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
    "AssocModuleGroupController",
    "AssocUserGroupController",
    "AssocViewControllerController",
    "ControllerController",
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
