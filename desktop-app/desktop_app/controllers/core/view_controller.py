from controllers.base.base_view_controller import BaseViewController
from schemas.core.module_schema import ModulePlainSchema
from schemas.core.view_schema import ViewPlainSchema, ViewStrictSchema
from services.core import ModuleService, ViewService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.view_view import ViewView
from events.events import ViewRequested


class ViewController(BaseViewController[ViewService, ViewView, ViewPlainSchema, ViewStrictSchema]):
    _plain_schema_cls = ViewPlainSchema
    _strict_schema_cls = ViewStrictSchema
    _service_cls = ViewService
    _view_cls = ViewView
    _endpoint = Endpoint.VIEWS
    _view_key = View.VIEWS

    def __init__(self, context):
        super().__init__(context)
        self.__module_service = ModuleService(self._settings, self._logger, self._tokens_accessor)

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ViewView:
        modules = await self.__module_service.get_all(Endpoint.MODULES, None, None, None, self._module_id)
        module_pairs = [(module.id, module.key) for module in modules]
        return ViewView(self, translation, mode, event.view_key, event.data, module_pairs)
