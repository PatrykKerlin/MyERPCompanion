from models.core.group import Group
from models.core.language import Language
from models.core.theme import Theme
from repositories.core import GroupRepository, LanguageRepository, ThemeRepository
from schemas.core.group_schema import GroupPlainSchema, GroupStrictSchema
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.theme_schema import ThemePlainSchema, ThemeStrictSchema
from services.core.module_service import ModuleService
from services.core.translation_service import TranslationService
from services.core.user_service import UserService
from services.core.view_service import ViewService
from utils.service_factory import ServiceFactory

GroupService = ServiceFactory.create(
    model_cls=Group,
    repository_cls=GroupRepository,
    input_schema_cls=GroupStrictSchema,
    output_schema_cls=GroupPlainSchema,
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


__all__ = [
    "GroupService",
    "LanguageService",
    "ModuleService",
    "ThemeService",
    "TranslationService",
    "UserService",
    "ViewService",
]
