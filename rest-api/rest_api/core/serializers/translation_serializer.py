from base.serializers.base_serializer import BaseSerializer
from ..models import Translation


class TranslationSerializer(BaseSerializer):
    class Meta:
        model = Translation

    def _get_list_fields(self):
        return ['language', 'value']
