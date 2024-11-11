from django.apps import apps
from base.serializers import SerializerFactory

LabelSerializer = SerializerFactory.get(apps.get_model('core', 'Label'), ['name'])
TranslationSerializer = SerializerFactory.get(apps.get_model('core', 'Translation'), ['language', 'value'])
ImageSerializer = SerializerFactory.get(apps.get_model('core', 'Image'), ['name'])
LanguageSerializer = SerializerFactory.get(apps.get_model('core', 'Language'), ['name', 'value'])
ModuleSerializer = SerializerFactory.get(apps.get_model('core', 'Module'), ['name'])
ViewSerializer = SerializerFactory.get(apps.get_model('core', 'View'), ['name'])

from .user_serializer import UserSerializer
from .token_serializer import TokenSerializer
from .label_translations_serializer import LabelTranslationsSerializer
from .view_labels_serializer import ViewLabelsSerializer
from .view_images_serializer import ViewImagesSerializer
from .view_content_serializer import ViewContentSerializer
from .menu_content_serializer import MenuContentSerializer
