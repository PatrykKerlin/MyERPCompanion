from base.serializers.base_serializer import BaseSerializer
from .field_serializer import FieldSerializer
from .text_serializer import TextSerializer
from ..models import FieldTexts


class FieldTextsSerializer(BaseSerializer):
    field = FieldSerializer()
    text = TextSerializer()

    class Meta:
        model = FieldTexts

    def _get_list_fields(self):
        return ['field', 'text']
