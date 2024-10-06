from base.serializers.base_serializer import BaseSerializer
from ..models import Field


class FieldSerializer(BaseSerializer):
    class Meta:
        model = Field

    def _get_list_fields(self):
        return ['name']
