from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateAppSchema
from utils.service_factory import ServiceFactory


LanguageService = ServiceFactory.create(
    name_prefix="Language",
    plain_schema_cls=LanguagePlainSchema,
    strict_schema_cls=LanguageStrictSchema,
)
UserService = ServiceFactory.create(
    name_prefix="User",
    plain_schema_cls=UserPlainSchema,
    strict_schema_cls=UserStrictUpdateAppSchema,
)

__all__ = [
    "LanguageService",
    "UserService",
]
