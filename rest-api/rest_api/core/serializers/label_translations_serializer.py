from base.serializers.base_serializer import BaseSerializer
from .label_serializer import LabelSerializer
from .translation_serializer import TranslationSerializer
from ..models import LabelTranslations


class LabelTranslationsSerializer(BaseSerializer):
    label = LabelSerializer()
    translation = TranslationSerializer()

    class Meta:
        model = LabelTranslations

    def _get_list_fields(self):
        return ['label', 'translation']
