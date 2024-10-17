from base.serializers.base_serializer import BaseSerializer
from ..models import Label


class LabelSerializer(BaseSerializer):
    class Meta:
        model = Label

    def _get_list_fields(self):
        return ['name']
