from typing import Dict

from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.conf import settings

from ..models import View, Label


class ViewContentSerializer(ModelSerializer):
    module = SerializerMethodField('get_module')
    label = SerializerMethodField('get_label')
    language = SerializerMethodField('get_language')
    theme = SerializerMethodField('get_theme')
    labels = SerializerMethodField('get_view_labels')
    images = SerializerMethodField('get_view_images')

    class Meta:
        model = View
        fields = ['module', 'label', 'name', 'template', 'order', 'language', 'theme', 'labels', 'images']

    @staticmethod
    def get_module(instance) -> str | None:
        if not instance.module:
            return None
        return instance.module.name

    def get_label(self, instance) -> str | None:
        if not instance.label:
            return None

        language = self.context.get('language', 'en')
        translation = Label.objects.get_translation_by_language(instance.label, language)

        return translation

    def get_view_labels(self, instance) -> Dict[str, Dict[str, str]]:
        language = self.context.get('language', 'en')

        labels = instance.fields.all()

        result = {}
        for label in labels:
            translation = Label.objects.get_translation_by_language(label, language)

            result[label.name] = {
                'value': translation
            }

        return result

    @staticmethod
    def get_view_images(instance) -> Dict[str, Dict[str, str]]:
        images = instance.images.all()

        result = {}
        for image in images:
            full_url = f'{settings.PROTOCOL}://{settings.ALLOWED_HOSTS[0]}:{settings.PORT}{image.image.url}'
            result[image.name] = {
                'value': full_url
            }

        return result

    def get_language(self, _) -> str:
        return self.context.get('language', 'en')

    def get_theme(self, _) -> str:
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            return user.theme

        return 'dark'