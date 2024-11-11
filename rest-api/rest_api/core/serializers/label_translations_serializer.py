from base.serializers import BaseSerializer
from . import LabelSerializer, TranslationSerializer
from ..models import LabelTranslations


class LabelTranslationsSerializer(BaseSerializer):
    label = LabelSerializer()
    translation = TranslationSerializer()

    class Meta:
        model = LabelTranslations

    @staticmethod
    def _get_list_fields():
        return ['label', 'translation']
