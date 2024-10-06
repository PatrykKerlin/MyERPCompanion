from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.conf import settings

from ..models import Page, Text
from ..helpers.model_fields import ModelFields


class PageContentSerializer(ModelSerializer):
    language = SerializerMethodField('get_language')
    theme = SerializerMethodField('get_theme')
    fields = SerializerMethodField('get_page_fields')
    images = SerializerMethodField('get_page_images')

    class Meta:
        model = Page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.fields = ModelFields.get_model_specific_fields(self.Meta.model) + ['language', 'theme', 'fields',
                                                                                     'images']

    def get_page_fields(self, page):
        language = self.context.get('language')

        fields = page.fields.all()

        result = {}
        for field in fields:
            text = field.texts.filter(language=language).first()

            if not text:
                text = field.texts.filter(language='en').first()

            if text:
                result[field.name] = {
                    'value': text.value
                }

        return result

    def get_page_images(self, page):
        images = page.images.all()

        result = {}
        for image in images:
            full_url = f'{settings.PROTOCOL}://{settings.ALLOWED_HOSTS[0]}:{settings.PORT}{image.image.url}'
            result[image.name] = {
                'value': full_url
            }

        return result

    def get_language(self, page):
        return self.context.get('language')

    def get_theme(self, page):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            return user.theme

        return 'dark'
