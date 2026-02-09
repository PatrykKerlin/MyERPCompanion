from schemas.core.translation_schema import TranslationPlainSchema, TranslationStrictSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class TranslationService(BaseService[TranslationPlainSchema, TranslationStrictSchema]):
    _plain_schema_cls = TranslationPlainSchema
    _strict_schema_cls = TranslationStrictSchema

    async def fetch_translation_items(self, path_param: str) -> dict[str, str]:
        page = 1
        translation: dict[str, str] = {}

        while True:
            response = await self._get(f"{Endpoint.TRANSLATIONS_BY_LANGUAGE}/{path_param}", query_params={"page": page})
            data = response.json()
            translation.update({item["key"]: item["value"] for item in data.get("items", [])})
            if not data.get("has_next", False):
                break
            page += 1

        return translation
