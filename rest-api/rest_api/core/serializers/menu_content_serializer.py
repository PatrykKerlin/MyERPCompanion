from typing import List, Dict

from rest_framework.serializers import Serializer, SerializerMethodField

from ..models.label_model import Label


class MenuContentSerializer(Serializer):
    name = SerializerMethodField('get_name')
    label = SerializerMethodField('get_label')
    pages = SerializerMethodField('get_pages')

    class Meta:
        fields = ['name', 'label', 'pages']

    @staticmethod
    def get_name(instance) -> str:
        return instance.name

    def get_label(self, instance) -> str:
        language = self.context.get('language', 'en')
        translation = Label.objects.get_translation_by_language(instance.label, language)

        return translation.value

    def get_pages(self, instance) -> List[Dict[str, str]]:
        language = self.context.get('language', 'en')
        pages = instance.pages.all().order_by('order')

        result = []
        for page in pages:
            translation = Label.objects.get_translation_by_language(page.label, language)

            page_data = {
                'name': page.name,
                'label': translation.value
            }

            result.append(page_data)

        return result
