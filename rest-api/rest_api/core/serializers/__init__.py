from django.apps import apps
from base.serializers import SerializerFactory
from base.serializers import SerializerM2MFactory

LabelSerializer = SerializerFactory.get(apps.get_model('core', 'Label'), ['name'])
TranslationSerializer = SerializerFactory.get(apps.get_model('core', 'Translation'), ['language', 'value'])
ImageSerializer = SerializerFactory.get(apps.get_model('core', 'Image'), ['name'])
ModuleSerializer = SerializerFactory.get(apps.get_model('core', 'Module'), ['name'])
ViewSerializer = SerializerFactory.get(apps.get_model('core', 'View'), ['name'])

ViewLabelsSerializer = SerializerM2MFactory.get(apps.get_model('core', 'ViewLabels'), ['view', 'label'],
                                                {'view': ViewSerializer, 'label': LabelSerializer})
ViewImagesSerializer = SerializerM2MFactory.get(apps.get_model('core', 'ViewImages'), ['view', 'image'],
                                                {'view': ViewSerializer, 'image': ImageSerializer})

from .user_serializer import UserSerializer
from .token_serializer import TokenSerializer
# from .view_content_serializer import ViewContentSerializer
# from .menu_content_serializer import MenuContentSerializer
