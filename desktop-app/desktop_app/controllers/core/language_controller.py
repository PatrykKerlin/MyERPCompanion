from controllers.base.base_view_controller import BaseViewController
from events.events import ViewRequested
from schemas.core.language_schema import LanguagePlainSchema, LanguageStrictSchema
from services.core import LanguageService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.language_view import LanguageView


class LanguageController(BaseViewController[LanguageService, LanguageView, LanguagePlainSchema, LanguageStrictSchema]):
    _plain_schema_cls = LanguagePlainSchema
    _strict_schema_cls = LanguageStrictSchema
    _service_cls = LanguageService
    _view_cls = LanguageView
    _endpoint = Endpoint.LANGUAGES
    _view_key = View.LANGUAGES

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> LanguageView:
        return LanguageView(self, translation, mode, event.view_key, event.data)
