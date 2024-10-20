from base.serializers.base_serializer import BaseSerializer
from ..models import Language


class LanguageSerializer(BaseSerializer):
    class Meta:
        model = Language

    def _get_list_fields(self):
        return ['name', 'value']
