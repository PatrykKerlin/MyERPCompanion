from django.apps import apps
from base.admin import AdminRegistrar

AdminRegistrar.register(apps.get_model('core', 'Module'), ['name'])
AdminRegistrar.register(apps.get_model('core', 'View'), ['name', 'template'])
AdminRegistrar.register(apps.get_model('core', 'Language'), ['name', 'value'])
AdminRegistrar.register(apps.get_model('core', 'Label'), ['name'])
AdminRegistrar.register(apps.get_model('core', 'Translation'), ['language', 'value'])
AdminRegistrar.register(apps.get_model('core', 'ViewLabels'), ['view', 'label'])
AdminRegistrar.register(apps.get_model('core', 'LabelTranslations'), ['label', 'translation'])
AdminRegistrar.register(apps.get_model('core', 'Image'), ['name', 'image'])
AdminRegistrar.register(apps.get_model('core', 'ViewImages'), ['view', 'image'])

from .user_admin import UserAdmin
