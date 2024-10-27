from typing import Dict

from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.conf import settings

from ..models import Page, Translation, Language


# from ..helpers.model_fields import ModelFields


class PageContentSerializer(ModelSerializer):
    module = SerializerMethodField('get_module')
    label = SerializerMethodField('get_label')
    language = SerializerMethodField('get_language')
    theme = SerializerMethodField('get_theme')
    labels = SerializerMethodField('get_page_labels')
    images = SerializerMethodField('get_page_images')

    class Meta:
        model = Page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.fields = ['module', 'label', 'name', 'template', 'order', 'language', 'theme', 'labels', 'images']

    def get_module(self, page) -> str | None:
        if not page.module:
            return None
        return page.module.name

    def get_label(self, page) -> str | None:
        if not page.label:
            return None

        language = self.context.get('language')
        translation = page.label.translations.filter(language__value=language).first()

        if not translation:
            translation = page.label.translations.filter(language__value='en').first()

        return translation.value

    def get_page_labels(self, page) -> Dict[str, Dict[str, str]]:
        language = self.context.get('language')

        labels = page.labels.all()

        result = {}
        for label in labels:
            translation = label.translations.filter(language__value=language).first()

            if not translation:
                translation = label.translations.filter(language__value='en').first()

            result[label.name] = {
                'value': translation.value
            }

        return result

    def get_page_images(self, page) -> Dict[str, Dict[str, str]]:
        images = page.images.all()

        result = {}
        for image in images:
            full_url = f'{settings.PROTOCOL}://{settings.ALLOWED_HOSTS[0]}:{settings.PORT}{image.image.url}'
            result[image.name] = {
                'value': full_url
            }

        return result

    def get_language(self, page) -> str:
        return self.context.get('language')

    def get_theme(self, page) -> str:
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            return user.theme

        return 'dark'
