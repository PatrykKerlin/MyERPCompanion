from controllers.base.base_view_controller import BaseViewController
from schemas.business.logistic.category_schema import CategoryPlainSchema, CategoryStrictSchema
from services.business.logistic import CategoryService
from utils.enums import Endpoint, View, ViewMode
from utils.translation import Translation
from views.business.logistic.category_view import CategoryView
from events.events import ViewRequested


class CategoryController(BaseViewController[CategoryService, CategoryView, CategoryPlainSchema, CategoryStrictSchema]):
    _plain_schema_cls = CategoryPlainSchema
    _strict_schema_cls = CategoryStrictSchema
    _service_cls = CategoryService
    _view_cls = CategoryView
    _endpoint = Endpoint.CATEGORIES
    _view_key = View.CATEGORIES

    async def _build_view(self, translation: Translation, mode: ViewMode, event: ViewRequested) -> CategoryView:
        return CategoryView(self, translation, mode, event.view_key, event.data)
