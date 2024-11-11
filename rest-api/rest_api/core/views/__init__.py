from base.views import ViewFactory
from ..serializers import *

ModuleView = ViewFactory.get(apps.get_model('core', 'Module'), ModuleSerializer)
ViewView = ViewFactory.get(apps.get_model('core', 'View'), ViewSerializer)
ImageView = ViewFactory.get(apps.get_model('core', 'Image'), ImageSerializer)
LabelView = ViewFactory.get(apps.get_model('core', 'Label'), LabelSerializer)
LanguageView = ViewFactory.get(apps.get_model('core', 'Language'), LanguageSerializer)
TranslationView = ViewFactory.get(apps.get_model('core', 'Translation'), TranslationSerializer)
LabelTranslationsView = ViewFactory.get(apps.get_model('core', 'LabelTranslations'), LabelTranslationsSerializer)
ViewImagesView = ViewFactory.get(apps.get_model('core', 'ViewImages'), ViewImagesSerializer)
ViewLabelsView = ViewFactory.get(apps.get_model('core', 'ViewLabels'), ViewLabelsSerializer)

from .health_check_view import HealthCheckView
from .token_view import TokenView
from .current_user_view import CurrentUserView
from .user_view import UserView
from .view_content_view import ViewContentView
from .menu_content_view import MenuContentView
