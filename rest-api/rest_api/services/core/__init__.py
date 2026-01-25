from models.core.assoc_module_group import AssocModuleGroup
from models.core.assoc_user_group import AssocUserGroup
from models.core.assoc_view_controller import AssocViewController
from models.core.controller import Controller
from models.core.group import Group
from models.core.language import Language
from models.core.theme import Theme
from models.core.view import View
from repositories.core import (
    AssocModuleGroupRepository,
    AssocUserGroupRepository,
    AssocViewControllerRepository,
    ControllerRepository,
    GroupRepository,
    LanguageRepository,
    ThemeRepository,
    ViewRepository,
)
from schemas.core.assoc_module_group_schema import AssocModuleGroupPlainSchema, AssocModuleGroupStrictSchema
from schemas.core.assoc_user_group_schema import AssocUserGroupPlainSchema, AssocUserGroupStrictSchema
from schemas.core.assoc_view_controller_schema import AssocViewControllerPlainSchema, AssocViewControllerStrictSchema
from schemas.core.controller_schema import ControllerPlainSchema, ControllerStrictSchema
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.theme_schema import ThemePlainSchema, ThemeStrictSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core.image_service import ImageService
from services.core.module_service import ModuleService
from services.core.translation_service import TranslationService
from services.core.user_service import UserService
from utils.service_factory import ServiceFactory

GroupService = ServiceFactory.create(
    model_cls=Group,
    repository_cls=GroupRepository,
    input_schema_cls=GroupStrictSchema,
    output_schema_cls=GroupPlainSchema,
)
AssocModuleGroupService = ServiceFactory.create(
    model_cls=AssocModuleGroup,
    repository_cls=AssocModuleGroupRepository,
    input_schema_cls=AssocModuleGroupStrictSchema,
    output_schema_cls=AssocModuleGroupPlainSchema,
)
AssocUserGroupService = ServiceFactory.create(
    model_cls=AssocUserGroup,
    repository_cls=AssocUserGroupRepository,
    input_schema_cls=AssocUserGroupStrictSchema,
    output_schema_cls=AssocUserGroupPlainSchema,
)
AssocViewControllerService = ServiceFactory.create(
    model_cls=AssocViewController,
    repository_cls=AssocViewControllerRepository,
    input_schema_cls=AssocViewControllerStrictSchema,
    output_schema_cls=AssocViewControllerPlainSchema,
)
ControllerService = ServiceFactory.create(
    model_cls=Controller,
    repository_cls=ControllerRepository,
    input_schema_cls=ControllerStrictSchema,
    output_schema_cls=ControllerPlainSchema,
)
LanguageService = ServiceFactory.create(
    model_cls=Language,
    repository_cls=LanguageRepository,
    input_schema_cls=LanguageStrictSchema,
    output_schema_cls=LanguagePlainSchema,
)
ThemeService = ServiceFactory.create(
    model_cls=Theme,
    repository_cls=ThemeRepository,
    input_schema_cls=ThemeStrictSchema,
    output_schema_cls=ThemePlainSchema,
)
ViewService = ServiceFactory.create(
    model_cls=View,
    repository_cls=ViewRepository,
    input_schema_cls=ViewStrictSchema,
    output_schema_cls=ViewPlainSchema,
)


__all__ = [
    "AssocModuleGroupService",
    "AssocUserGroupService",
    "AssocViewControllerService",
    "ControllerService",
    "GroupService",
    "ImageService",
    "LanguageService",
    "ModuleService",
    "ThemeService",
    "TranslationService",
    "UserService",
    "ViewService",
]
