from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateSchema
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
    strict_schema_cls=UserStrictUpdateSchema,
)
ViewService = ServiceFactory.create(
    name_prefix="View",
    plain_schema_cls=ViewPlainSchema,
    strict_schema_cls=ViewStrictSchema,
)


__all__ = [
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
