from typing import List, Dict

from rest_framework.serializers import Serializer, SerializerMethodField

from ..models.label_model import Label


class MenuContentSerializer(Serializer):
    name = SerializerMethodField('get_name')
    label = SerializerMethodField('get_label')
    views = SerializerMethodField('get_views')

    class Meta:
        fields = ['name', 'label', 'views']

    @staticmethod
    def get_name(instance) -> str:
        return instance.name

    def get_label(self, instance) -> str:
        language = self.context.get('language', 'en')
        translation = Label.objects.get_translation_by_language(instance.label, language)

        return translation

    def get_views(self, instance) -> List[Dict[str, str]]:
        language = self.context.get('language', 'en')
        views = instance.views.all().order_by('order')

        result = []
        for view in views:
            translation = Label.objects.get_translation_by_language(view.label, language)

            view_data = {
                'name': view.name,
                'label': translation
            }

            result.append(view_data)

        return result
