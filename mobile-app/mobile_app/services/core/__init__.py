from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from services.core.app_service import AppService
from services.core.auth_service import AuthService
from services.core.translation_service import TranslationService
from utils.service_factory import ServiceFactory

LanguageService = ServiceFactory.create(
    name_prefix="Language",
    plain_schema_cls=LanguagePlainSchema,
    strict_schema_cls=LanguageStrictSchema,
)

__all__ = [
    "AppService",
    "AuthService",
    "LanguageService",
    "TranslationService",
]
