from base.serializers.base_serializer import BaseSerializer
from ..models import Image


class ImageSerializer(BaseSerializer):
    class Meta:
        model = Image

    def _get_list_fields(self):
        return ['name']
