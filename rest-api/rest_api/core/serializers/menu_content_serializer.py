from rest_framework.serializers import Serializer, SerializerMethodField
from ..models import Module, Page, Translation


class MenuContentSerializer(Serializer):
    name = SerializerMethodField('get_name')
    label = SerializerMethodField('get_label')
    pages = SerializerMethodField('get_pages')

    class Meta:
        model = Module
        fields = ['name', 'label', 'pages']

    def get_name(self, obj):
        return obj.name

    def get_label(self, obj):
        language = self.context.get('language', 'en')
        translation = obj.label.translations.filter(language=language).first()

        return translation.value

    def get_pages(self, obj):
        language = self.context.get('language', 'en')
        pages = obj.pages.all()

        result = []
        for page in pages:
            translation = page.label.translations.filter(language=language).first()

            page_data = {
                'name': page.name,
                'label': translation.value
            }

            result.append(page_data)

        return result
