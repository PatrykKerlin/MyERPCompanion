from models.core import Group, Language, Theme, View
from repositories.core import GroupRepository, LanguageRepository, ThemeRepository
from schemas.core import (
    GroupPlainSchema,
    GroupStrictSchema,
    LanguagePlainSchema,
    LanguageStrictSchema,
    ThemePlainSchema,
    ThemeStrictSchema,
)
from utils.factories import ServiceFactory

from .module_service import ModuleService
from .translation_service import TranslationService
from .user_service import UserService
from .view_service import ViewService


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
