from controllers.base.base_view_controller import BaseViewController
from schemas.core.module_schema import ModulePlainSchema, ModuleStrictSchema
from services.core import ModuleService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.core.module_view import ModuleView
from events.events import ViewRequested


class ModuleController(BaseViewController[ModuleService, ModuleView, ModulePlainSchema, ModuleStrictSchema]):
    _plain_schema_cls = ModulePlainSchema
    _strict_schema_cls = ModuleStrictSchema
    _service_cls = ModuleService
    _view_cls = ModuleView
    _endpoint = Endpoint.MODULES
    _view_key = View.MODULES

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> ModuleView:
        return ModuleView(self, translation, mode, event.view_key, event.data)
