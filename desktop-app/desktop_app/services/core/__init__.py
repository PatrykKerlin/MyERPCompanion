from schemas.core.assoc_module_group_schema import AssocModuleGroupPlainSchema, AssocModuleGroupStrictSchema
from schemas.core.assoc_user_group_schema import AssocUserGroupPlainSchema, AssocUserGroupStrictSchema
from schemas.core.assoc_view_controller_schema import AssocViewControllerPlainSchema, AssocViewControllerStrictSchema
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateAppSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core.app_service import AppService
from services.core.auth_service import AuthService
from services.core.image_service import ImageService
from services.core.translation_service import TranslationService
from utils.service_factory import ServiceFactory

GroupService = ServiceFactory.create(
    name_prefix="Group",
    plain_schema_cls=GroupPlainSchema,
    strict_schema_cls=GroupStrictSchema,
)
LanguageService = ServiceFactory.create(
    name_prefix="Language",
    plain_schema_cls=LanguagePlainSchema,
    strict_schema_cls=LanguageStrictSchema,
)
ModuleService = ServiceFactory.create(
    name_prefix="Module",
    plain_schema_cls=ModulePlainSchema,
    strict_schema_cls=ModuleStrictSchema,
)
UserService = ServiceFactory.create(
    name_prefix="User",
    plain_schema_cls=UserPlainSchema,
    strict_schema_cls=UserStrictUpdateAppSchema,
)
ViewService = ServiceFactory.create(
    name_prefix="View",
    plain_schema_cls=ViewPlainSchema,
    strict_schema_cls=ViewStrictSchema,
)

AssocModuleGroupService = ServiceFactory.create(
    name_prefix="AssocModuleGroup",
    plain_schema_cls=AssocModuleGroupPlainSchema,
    strict_schema_cls=AssocModuleGroupStrictSchema,
)
AssocUserGroupService = ServiceFactory.create(
    name_prefix="AssocUserGroup",
    plain_schema_cls=AssocUserGroupPlainSchema,
    strict_schema_cls=AssocUserGroupStrictSchema,
)
AssocViewControllerService = ServiceFactory.create(
    name_prefix="AssocViewController",
    plain_schema_cls=AssocViewControllerPlainSchema,
    strict_schema_cls=AssocViewControllerStrictSchema,
)

__all__ = [
    "AssocModuleGroupService",
    "AssocUserGroupService",
    "AssocViewControllerService",
    "AppService",
    "AuthService",
    "GroupService",
    "ImageService",
    "LanguageService",
    "ModuleService",
    "TranslationService",
    "UserService",
    "ViewService",
]
