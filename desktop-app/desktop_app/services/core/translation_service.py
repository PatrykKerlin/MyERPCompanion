from config.enums import Endpoint
from services.base.base_service import BaseService


class TranslationService(BaseService):
    async def fetch_translations(self, language: str) -> dict[str, str]:
        page = 1
        page_size = 100
        translation: dict[str, str] = {}

        while True:
            response = await self._get(
                f"{Endpoint.TRANSLATIONS_BY_LANGUAGE}/{language}",
                params={"page": page, "page_size": page_size},
            )
            data = response.json()
            translation.update({item["key"]: item["value"] for item in data.get("items", [])})
            if not data.get("has_next", False):
                break
            page += 1

        return translation
